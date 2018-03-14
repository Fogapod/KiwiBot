from objects.modulebase import ModuleBase

from utils.funcs import find_user

from discord import Embed


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [user]'
    short_doc = 'Get information about matched user.'

    name = 'user'
    aliases = (name, )

    async def on_call(self, msg, *args, **flags):
        if len(args) == 1:
            user = msg.author
        else:
            user = await find_user(
                msg.content.partition(args[0])[2].lstrip(),
                msg, self.bot
            )

        if user is None:
            return '{warning} User not found'

        return f'`{user} {user.id}`'