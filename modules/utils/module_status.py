from modules.modulebase import ModuleBase

from discord import Game

class Module(ModuleBase):
    """{prefix}{keywords} [type] [status]

    Update bot status.

    Status types:
        playing (default)
        streaming
        listening
        watching
    
    *Leave empty to remove status

    {protection} or higher permission level required to use"""

    name = 'status'
    keywords = (name, )
    arguments_required = 0
    protection = 2

    async def on_permission_denied_text(self, msg):
        return 'not dogsong or notsosuper'

    async def on_load(self, from_reload):
        last_status = self.bot.config.get('last_status', '')
        last_status_type = self.bot.config.get('last_status_type', 0)

        if last_status:
            presence = Game(name=last_status, type=last_status_type)
            await self.bot.change_presence(game=presence)

    async def on_call(self, msg, *args, **options):
        status = ''

        if len(args) == 1:
            presence = Game(name='')
        else:
            subcommand = args[1].lower()
            status = ' '.join(args[2:])

            if subcommand == 'playing':
                presence = Game(name=status)
            elif subcommand == 'streaming':
                presence = Game(name=status, type=1)
            elif subcommand == 'listening':
                presence = Game(name=status, type=2)
            elif subcommand == 'watching':
                presence = Game(name=status, type=3)
            else:
                status = ' '.join(args[1:])
                presence = Game(name=status)

        await self.bot.change_presence(game=presence)
        await self.bot.config.put('last_status', status)
        await self.bot.config.put('last_status_type', presence.type)

        return 'Status changed to `' + presence.name + '`' if presence.name else 'Status removed'