from modules.modulebase import ModuleBase

from discord import Game

class Module(ModuleBase):
    """{prefix}{keywords} <status>
    
    Set bot status.

    {protection} or higher permission level required to use"""

    name = 'status'
    keywords = (name, 'playing')
    arguments_required = 0
    protection = 2

    @property
    def permission_denied_text(self):
        return 'not dogsong or notsosuper'

    async def on_load(self):
        previous_status = self.bot.config.get('previous_status', '')

        if previous_status:
            await self.bot.change_presence(game=Game(name=previous_status))

    async def on_call(self, message, *args):
        status = message.content[len(args[0]):].strip()

        await self.bot.change_presence(game=Game(name=status))
        await self.bot.config.put('previous_status', status)

        return 'Status changed to `' + status + '`' if status else 'Status removed'