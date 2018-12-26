class ArgParser:

    def __init__(self, string, ctx):
        self.ctx = ctx

        self.args = []
        self.args_raw = []
        self.flags = {}
        self._separators = []

        self._split(string)

    @classmethod
    def parse(cls, string, ctx):
        return cls(string, ctx)

    def _split(self, string):
        args, seps = [], []
        index = 0
        quote = None
        is_previous_space = True

        s = string.strip()

        while s:
            q_buff = ''
            c = s[:1]

            while c in ('\'', '"'):
                if not q_buff or q_buff[0] == c:
                    q_buff += c
                else:
                    break

                if len(s) > len(q_buff):
                    c = s[len(q_buff)]
                else:
                    c = ''

            s = s[len(q_buff):]

            if quote == q_buff and s and s[0].isspace():
                quote = None
            elif quote is None and q_buff and is_previous_space:
                quote = q_buff
            elif q_buff:
                c = q_buff + c

            if c.isspace() and not quote:
                if is_previous_space:
                    seps[index - 1] += c
                else:
                    seps.append(c)
                    index += 1
                is_previous_space = True
            elif c != quote:
                if is_previous_space:
                    args.append(c)
                else:
                    args[index] += c
                is_previous_space = False

            s = s[1:]

            # print(f'Char {"[" + c + "]":<3} Str {"[" + s + "]":<20} Quote {quote}')

        self.args_raw = args
        self.args = args
        self._separators = seps

        return args, seps

    async def parse_flags(self, known_flags=()):
        args = []
        seps = []
        flags = {}
        flag = ''

        async def try_to_add_flag(name, arg=''):
            flag = name
            for f in known_flags:
                if name in (f.name, f.alias):
                    flag = f

            if not flag:
                return 0

            if isinstance(flag, str):  # unknown flag
                flags[flag] = True
                return 0

            if flag.is_bool:
                flags[flag.name] = True
                return 0
            else:
                flags[flag.name] = await flag.convert(arg, self.ctx)
                return 1

        for i, arg in enumerate(self.args_raw + ['']):
            if await try_to_add_flag(flag, arg):
                flag = ''
                continue

            flag = ''

            if arg[:1] == '-' and arg != '-':
                if arg[:2] == '--':
                    flag = arg[2:]
                    if not flag:
                        args += self.args_raw[i + 1:] + ['']
                        if i > 0:
                            seps += self._separators[i - 1:]
                        break
                else:
                    for c in arg[1:-1]:
                        await try_to_add_flag(c)

                    flag = arg[-1]
            else:
                args.append(arg)
                if i > 0 and len(self._separators) >= i:
                    seps.append(self._separators[i - 1])

        self.args_raw = args[:-1] if args and not args[-1] else args  # last flag can eat empty argument from end
        self._separators = seps
        self.flags = flags

        return flags

    async def convert_args(self, converters):
        converted = [self.args[0]]

        for i, arg in enumerate(self.args[1:]):
            if i + 1 > len(converters):
                converted.append(arg)
            else:
                converted.append(await converters[i].convert(arg, self.ctx))

        self.args = converted

        return self.args

    def __len__(self):
        return len(self.args)

    def __bool__(self):
        return len(self.args) != 0

    def __str__(self):
        return str(self.args)

    def __getitem__(self, value):
        if isinstance(value, slice):
            if value.step is not None:
                raise ValueError('Arguments object does not support slicing with step')

            seps = self._separators + ['']
            result = ''

            start = value.start or 0
            end = value = value.stop or len(self.args_raw)

            if start < 0:
                start = len(self.args_raw) + start
            if end < 0:
                end = len(self.args_raw) + end

            for i in range(start, end):
                result += self.args_raw[i] + (seps[i] if i != end - 1 else '')
            return result
        else:
            return self.args[value]
