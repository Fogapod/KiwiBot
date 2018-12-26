from parser.converters import String


class Argument:
    def __init__(self, name, hint=None, converter=String(), checks=(), optional=False):
        self.name = name

        if isinstance(converter, type):
            self.converter = converter()
        else:
            self.converter = converter

        if hint is None:
            self.hint = self.converter.pretty_name.lower()
        else:
            self.hint = hint

        self.checks = checks
        self.optional = optional

    @property
    def is_bool(self):
        return False

    async def run_checks(self, content, value):
        for check in self.checks:
            await check.run(self, content, value)

    async def convert(self, content, ctx):
        value = await self.converter.convert(content, ctx)

        await self.run_checks(content, value)

        return value

    def __str__(self):
        if self.optional:
            return f'[{self.hint}]'
        else:
            return f'<{self.hint}]'

    def __repr__(self):
        return f'<{self.__class__.__name__} name={self.name!r} converter={self.converter!r}>'
