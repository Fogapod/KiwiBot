from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

from copy import copy

from utils.funcs import find_user


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user> <command>'
    short_doc = 'Replace message author and run command'

    name = 'runas'
    aliases = (name, )
    category = 'Owner'
    min_args = 2
    user_perms = (PermissionBotOwner(), )
    guild_only = True
    hidden = True

    async def on_call(self, ctx, args, **flags):
        user = await find_user(args[1], ctx.message, strict_guild=True)

        if user is None:
            return '{warning} User not found'

        fake_msg = copy(ctx.message)
        fake_ctx = copy(ctx)

        fake_msg.author = user
        fake_ctx.author = user
        fake_ctx.msg = fake_msg

        await self.bot.process_command(fake_ctx, args[2:])

        return f'Message processed as `{user}`'