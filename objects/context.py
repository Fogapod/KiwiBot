class Context:
    __slots__ = ('bot', 'message', 'prefix', 'guild', 'channel', 'author', 'session', )

    def __init__(self, bot, msg, prefix):
        self.bot = bot
        self.message = msg
        self.prefix = prefix
        self.guild = msg.guild
        self.channel = msg.channel
        self.author = msg.author
        self.session = bot.sess

    @property
    def me(self):
        return self.guild.me if self.guild else self.bot.user

    @property
    def is_nsfw(self):
        return getattr(self.channel, 'is_nsfw', lambda: True)()

    async def info(self, content=None, send=True, **kwargs):
        s = f'ℹ {content or ""}'
        return await self.send(s, **kwargs) if send else s

    async def warn(self, content=None, send=True, **kwargs):
        s = f'⚠ {content or ""}'
        return await self.send(s, **kwargs) if send else s

    async def error(self, content=None, send=True, **kwargs):
        s = f'‼ {content or ""}'
        return await self.send(s, **kwargs) if send else s

    async def send(self, content=None, *, channel=None, register=True, **kwargs):
        channel = self.channel if channel is None else channel
        response_to = kwargs.pop('response_to', None) or self.message if register else None

        return await self.bot.send_message(
            channel, content, response_to=response_to, **kwargs)

    async def react(self, emoji, message=None, register=True, **kwargs):
        response_to = (kwargs.pop('response_to', None) or self.message) if register else None

        return await self.bot.add_reaction(
            message or self.message, emoji, response_to=response_to, **kwargs)
