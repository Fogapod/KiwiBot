from modules.modulebase import ModuleBase

from permissions import PermissionBotOwner
from utils.helpers import get_string_after_entry


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Respond with given text.'

    name = 'say'
    aliases = (name, 'echo')
    required_args = 1
    require_perms = (PermissionBotOwner, )
    hidden = True

    async def on_call(self, msg, *args, **options):
        await self.bot.send_message(
            msg, get_string_after_entry(args[0], msg.content),
            parse_content=False, response_to=msg
        )