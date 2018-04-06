from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

from utils.funcs import find_user, get_local_prefix


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user> <command>'
    short_doc = 'Force bot to think command was sent by matched user.'

    name = 'runas'
    aliases = (name, )
    guild_only = True
    required_args = 2
    require_perms = (PermissionBotOwner(), )
    hidden = True

    async def on_call(self, msg, args, **flags):
        user = await find_user(args[1], msg, self.bot, strict_guild=True)

        if user is None:
            return '{warning} User not found'

        prefix = await get_local_prefix(msg, self.bot)
        new_content = args[2:]

        msg.author = user
        msg.content = prefix + new_content
        await self.bot.on_message(msg)

        return f'Message processed as `{user}`'