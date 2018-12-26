import inspect

from objects.moduleexceptions import ArgParseError, ArgCheckError


class Check:
    '''Can be used with both Argument and Flag'''

    def __init__(self, check_func, error='Check {0.check.__name__} failed for {1.__class__.__name__ {1.name}'):
        self.check = check_func
        self.error = error

    @classmethod
    def between(cls, val1, val2):
        if val1 >= val2:
            raise ValueError("Second value is lower or equal to first")

        return cls(
            lambda flag, content, value: val1 <= value <= val2,
            'Value of {1.__class__.__name__} **{1.name}** should be between **%s** and **%s**' % (val1, val2)
        )

    @classmethod
    def less(cls, val):
        return cls(
            lambda flag, content, value: value < val,
            'Value of {1.__class__.__name__} **{1.name}** should be less than **%s**' % val
        )

    @classmethod
    def bigger(cls, val):
        return cls(
            lambda flag, content, value: value > val,
            'Value of {1.__class__.__name__} **{1.name}** should be bigger than **%s**' % val
        )

    async def run(self, argument, content, value):
        if inspect.iscoroutinefunction(self.check):
            result = await self.check(argument, content, value)
        else:
            result = self.check(argument, content, value)

        if not result:
            raise ArgCheckError(self.error.format(self, argument))
