from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

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
        user = await find_user(args[1], ctx.message, self.bot, strict_guild=True)

        if user is None:
            return '{warning} User not found'

        ctx.author = user

        await self.bot.process_command(ctx, args[2:])

        return f'Message processed as `{user}`'