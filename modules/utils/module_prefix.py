from modules.modulebase import ModuleBase

from utils.checks import get_user_access_level
from utils.constants import DEFAULT_PREFIXES


class Module(ModuleBase):
    """{prefix}{keywords} <subcommand>

    Manage bot prefix.

    Subcommands:
        current
        update [global] <prefix>
        reset [global]

    {protection} or higher permission level required to use"""

    name = 'prefix'
    keywords = (name, )
    arguments_required = 1
    protection = 0

    async def on_call(self, message, *args):
        subcommand = args[0].lower()
        if subcommand == 'current':
            return 'Current prefix is `' + self.bot.prefixes[0] + '`'

        if subcommand == 'update':
            if len(args) < 2:
                return self.not_enough_arguments_text
            if args[1].lower() == 'global':
                if len(args) < 3:
                    return self.not_enough_arguments_text
                if await get_user_access_level(self, message) < self.protection:
                    return self.permission_denied_text

                self.bot.prefixes[0] = message.content[message.content.index(args[2]) + len(args[2]):].strip()
            else:
                return '{warning} Not implemented'

        elif subcommand == 'reset':
            if len(args) == 2 and args[1].lower() == 'global':
                if await get_user_access_level(self, message) < self.protection:
                    return self.permission_denied_text

                self.bot.prefixes = DEFAULT_PREFIXES
            else:
                return '{warning} Not implemented'