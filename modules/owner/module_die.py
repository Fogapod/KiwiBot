from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

from constants import STOP_EXIT_CODE


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [exit_code]'
    short_doc = 'Stop bot.'

    name = 'stop'
    aliases = (name, 'die', '!')
    require_perms = (PermissionBotOwner(), )
    hidden = True

    async def on_call(self, message, args, **options):
        await message.add_reaction('✅')
        exit_code = args[1] if len(args) == 2 else STOP_EXIT_CODE
        self.bot.stop(exit_code)