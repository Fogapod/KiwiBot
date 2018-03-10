from modules.modulebase import ModuleBase

from utils.helpers import find_user, get_string_after_entry

from discord import Embed


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user>'
    short_doc = 'Get information about user.'

    name = 'user'
    aliases = (name, )

    async def on_call(self, msg, *args, **flags):
        user = None

        if len(args) == 1:
            user = msg.author
        else:
            user = await find_user(
                get_string_after_entry(args[0], msg.content),
                msg, self.bot
            )

        if user is None:
            return '{warning} User not found'

        return f'`{user} {user.id}`'