class Context:
    def __init__(self, bot, msg, prefix):
        self.bot = bot
        self.message = msg
        self.prefix = prefix
        self.guild = msg.guild
        self.channel = msg.channel
        self.author = msg.author

    @property
    def me(self):
        return self.guild.me if self.guild else self.bot.user

    async def send(self, content=None, *, channel=None, register=True, **kwargs):
        channel = self.channel if channel is None else channel
        response_to = self.message if register else None

        return await self.bot.send_message(
            channel, content, response_to=response_to, **kwargs)