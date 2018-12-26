import asyncio

from objects.moduleexceptions import ArgParseError

from utils.funcs import find_user


DEFAULT_CONVERT_ERROR_TEXT = 'Failed to convert `{0}` to **{1.pretty_name}**: {2.__class__.__name__}'

class Converter:

    greedy = False

    def __init__(self, error=DEFAULT_CONVERT_ERROR_TEXT):
        self.error = error

        self.pretty_name = getattr(self, 'pretty_name', self.__class__.__name__)

    async def convert(self, content, ctx):
        try:
            return await self._convert(content, ctx)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            raise ArgParseError(self.error.format(content, self, e))

    async def _convert(self, args, ctx):
        raise NotImplemented

    def is_bool(self):
        '''Temporary solution to fix import cycle'''
        return False


class Bool(Converter):
    @property
    def is_bool():
        return True

    async def _convert(self, content, ctx):
        positive = ['1', 'y', 'yes', '+', 'positive']
        negative = ['0', 'y', 'no',  '-', 'negative']
 
        lower_content = content.lower()

        for p in positive:
            if lower_content == p:
                return True

        for n in negative:
            if lower_content == n:
                return False

        raise ValueError


class Integer(Converter):
    async def _convert(self, content, ctx):
        return int(content)


class Number(Converter):
    async def _convert(self, context, ctx):
        return float(content)


class String(Converter):
    async def _convert(self, content, ctx):
        return content


class TernaryString(String):
    greedy = True


class Command(Converter):
    async def _convert(self, content, ctx):
        return ctx.bot.mm.modules['content']


class User(Converter):

    def __init__(self, **kwargs):
        super().__init__(kwargs.get('error', DEFAULT_CONVERT_ERROR_TEXT))

        self.additional_kwargs = kwargs

    async def _convert(self, content, ctx):
        value = await find_user(content, ctx.message, **self.additional_kwargs)

        if not value:
            raise ValueError

        return value
