class ArgParser:

    def __init__(self, string):
        self._args = []
        self._separators = []

        self._args, self._separators = self._split(string)

    def _split(self, string):
        args, seps = [], []
        index = 0
        is_previous_space = True
        last_c = ''
        opened_quote = None
        escape = False

        for c in string.strip():
            if last_c == '\\':
                escape = True
                if c == '\\':
                    c = ''
            else:
                escape = False 

            if c in ['"', '\'']:
                if escape:
                    args[index] = ''.join([ch for ch in args[index][:-1]])
                else:
                    if opened_quote is None:
                        opened_quote = c
                        last_c = c
                        continue
                    if opened_quote == c:
                        opened_quote = None
                        last_c = c
                        continue

            if c.isspace() and opened_quote is None:
                if is_previous_space:
                    seps[index - 1] += c
                else:
                    seps.append(c)
                    index += 1
                is_previous_space = True
            else:
                if is_previous_space:
                    args.append(c)
                else:
                    args[index] += c
                is_previous_space = False
            last_c = c

        return args, seps

    def __len__(self):
        return len(self._args)

    def __bool__(self):
        return len(self._args) != 0

    def __str__(self):
        return str(self._args)

    def __getitem__(self, value):
        if isinstance(value, slice):
            if value.step is not None:
                raise ValueError('Arguments object does not support slicing with step')
            result = ''
            for i in range(value.start or 0, value.stop or len(self._args)):
                result += self._args[i]
                if len(self._separators) > i:
                    result += self._separators[i]
            return result
        else:
            return self._args[value]