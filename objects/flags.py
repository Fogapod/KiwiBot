import inspect

from enum import Enum


class FlagType(Enum):
    BOOL           = 1
    INTEGER        = 2
    NUMBER         = 3
    STRING         = 4
    TERNARY_STRING = 5


class Flag:

    def __init__(self, name, alias, descr='', type=FlagType.STRING, checks=(), hidden=False):
        self.name = name
        self.alias = alias
        self.description = descr
        self.type = type
        self.checks = checks
        self.hidden = hidden

    async def run_checks(self, content, value):
        for check in self.checks:
            await check.run(self, content, value)

    async def convert(self, content):
        if self.type == FlagType.BOOL:
            value = True
        elif self.type == FlagType.INTEGER:
            try:
                value = int(content)
            except ValueError:
                raise FlagParseError(
                    f'**{self.name}** flag argument should be integer, failed to convert `{content}`')
        elif self.type == FlagType.Number:
            try:
                value = float(content)
            except ValueError:
                raise FlagParseError(
                    f'**{self.name}** flag argument should be a number, failed to convert `{content}`')
        elif self.type in (FlagType.STRING, FlagType.TERNARY_STRING):
            value = content
        else:
            raise FlaParseErroar(f'Unknown flag type passed: {self.type}')

        await self.run_checks(content, value)

        return value

    def doc_line(self):
        return f'\t[--{self.name}|-{self.alias}]: {self.description}'

    def __repr__(self):
        return f'<{self.__class__.__name__} name={self.name!r} type={self.type!r}>'


class Check:
    def __init__(self, check_func, error='Check {0.check.__name__} failed for flag {1.name}'):
        self.check = check_func
        self.error = error

    @classmethod
    def between(cls, val1, val2):
        if val1 >= val2:
            raise ValueError("Second value is lower or equal to first")

        return cls(
            lambda flag, content, value: val1 <= value <= val2,
            'Value of flag **{1.name}** should be between **%s** and **%s**' % (val1, val2)
        )

    @classmethod
    def less(cls, val):
        return cls(
            lambda flag, content, value: value < val,
            'Value of flag **{1.name}** should be less than **%s**' % val
        )

    @classmethod
    def bigger(cls, val):
        return cls(
            lambda flag, content, value: value > val,
            'Value of flag **{1.name}** should be bigger than **%s**' % val
        )

    async def run(self, flag, content, value):
        if inspect.iscoroutinefunction(self.check):
            result = await self.check(flag, content, value)
        else:
            result = self.check(flag, content, value)
        
        if not result:
            raise FlagCheckError(self.error.format(self, flag))


class FlagParseError(Exception):
    pass

class FlagCheckError(FlagParseError):
    pass
