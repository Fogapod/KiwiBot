from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

from utils.funcs import find_user, get_local_prefix

from copy import copy


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user> <command>'
    short_doc = 'Replace message author and run command'

    name = 'runas'
    aliases = (name, )
    min_args = 2
    user_perms = (PermissionBotOwner(), )
    guild_only = True
    hidden = True

    async def on_call(self, msg, args, **flags):
        user = await find_user(args[1], msg, self.bot, strict_guild=True)

        if user is None:
            return '{warning} User not found'

        prefix = await get_local_prefix(msg, self.bot)
        new_content = args[2:]

        new_msg = copy(msg)
        new_msg.author = user
        new_msg.content = prefix + new_content
        await self.bot.on_message(new_msg)

        return f'Message processed as `{user}`'