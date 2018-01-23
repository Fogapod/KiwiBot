from commands.commandbase import CommandBase

from discord import Game

class Command(CommandBase):
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

    async def on_call(self, message):
        status = ' '.join(message.content.strip().split(' ')[1:])

        await self.bot.change_presence(game=Game(name=status))
        await self.bot.config.put('previous_status', status)

        return 'Status changed to `' + status + '`' if status else 'Status removed'