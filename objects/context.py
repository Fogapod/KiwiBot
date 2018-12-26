class Context:
    __slots__ = ('bot', 'message', 'prefix', 'guild', 'channel', 'author', 'session', )

    def __init__(self, bot, message, prefix):
        self.bot = bot
        self.message = message
        self.prefix = prefix

        # shortcuts
        self.guild = message.guild
        self.channel = message.channel
        self.author = message.author
        self.session = bot.sess

    @property
    def me(self):
        return self.guild.me if self.guild else self.bot.user

    @property
    def is_nsfw(self):
        return getattr(self.channel, 'is_nsfw', lambda: True)()

    @property
    def from_edit(self):
        return self.message.edited_at is not None

    async def local_prefix(self):
        if self.guild is None:
            return self.bot._default_prefix

        guild_prefix = self.bot._guild_prefixes.get(self.guild.id)
        if guild_prefix is not None:
            return guild_prefix

    async def info(self, content=None, send=True, **kwargs):
        s = '\N{INFORMATION SOURCE}' + f'{content or ""}'
        return await self.send(s, **kwargs) if send else s

    async def warn(self, content=None, send=True, **kwargs):
        s = '\N{WARNING SIGN}' + f'{content or ""}'
        return await self.send(s, **kwargs) if send else s

    async def error(self, content=None, send=True, **kwargs):
        s = '\N{DOUBLE EXCLAMATION MARK}' + f'{content or ""}'
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

    def __repr__(self):
        return f'Context prefix={self.prefix!r}'
