from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageRoles

import discord

from utils.funcs import find_role


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <role>'
    short_doc = 'Make role a color role or reverse'

    name = 'makecolor'
    category = 'Discord'
    aliases = (name, 'makecolour')
    bot_perms = (PermissionManageRoles(), )
    user_perms = (PermissionManageRoles(), )
    guild_only = True
    min_args = 1

    async def on_call(self, ctx, args, **flags):
        role = await find_role(args[1:], ctx.guild)

        if role is None:
            return await ctx.warn('Role not found')

        if role.is_default():
            return await ctx.error('Unable to make @everyone a color role')

        if ctx.author != ctx.guild.owner:
            if role >= ctx.author.top_role:
                return await ctx.error('Role is higher or equal than your top role. Refused to manipulate')

            if role.permissions > ctx.author.guild_permissions:
                return await ctx.error('Role permissions are higher than yours. Refused to manipulate')

        is_a_color_role = await ctx.bot.pg.fetchval(
            "SELECT EXISTS(SELECT 1 FROM color_roles WHERE guild_id = $1 AND role_id = $2)",
            ctx.guild.id, role.id
        )

        if is_a_color_role:
            await ctx.bot.pg.fetch(
                "DELETE FROM color_roles WHERE guild_id = $1 AND role_id = $2",
                ctx.guild.id, role.id
            )

            await ctx.info(f'Removed **{role}** from the list of color roles')
        else:
            await ctx.bot.pg.fetch(
                "INSERT INTO color_roles (guild_id, role_id) VALUES($1, $2)",
                ctx.guild.id, role.id
            )

            await ctx.info(f'Added **{role}** to the list of color roles')
