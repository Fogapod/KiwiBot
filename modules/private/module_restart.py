from modules.modulebase import ModuleBase


class Module(ModuleBase):
    """{prefix}{keywords}
    
    Restart the bot.
    {protection} or higher permission level required to use"""

    name = 'restart'
    keywords = (name, )
    protection = 2

    async def on_call(self, message, *args):
        await self.bot.add_reaction(message, '✅')
        await self.bot.restart()