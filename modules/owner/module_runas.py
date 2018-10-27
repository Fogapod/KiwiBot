from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

from copy import copy

from utils.funcs import find_user, get_local_prefix


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user> <command>'
    short_doc = 'Replace message author and run command'
    long_doc = (
        'Flags:'
        '\t[--no-prefix|-n]: do not append prefix to the message'
    )

    name = 'runas'
    aliases = (name, )
    category = 'Owner'
    min_args = 2
    user_perms = (PermissionBotOwner(), )
    guild_only = True
    flags = {
        'no-prefix': {
            'alias': 'n',
            'bool': True
        }
    }
    hidden = True

    async def on_call(self, ctx, args, **flags):
        user = await find_user(args[1], ctx.message, strict_guild=True)

        if user is None:
            return await ctx.warn('User not found')

        fake_msg = copy(ctx.message)

        if flags.get('no-prefix', False):
            fake_msg.content = args[2:]
        else:
            fake_msg.content = await get_local_prefix(ctx) + args[2:]

        fake_msg.author = user

        await self.bot.on_message(fake_msg)

        return f'Message processed as `{user}`'
