from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageRoles

import discord

from utils.funcs import find_role


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [add|remove] [role_name]'
    short_doc = 'Assign or remove color role'
    long_doc = (
        'Subcommands:\n'
        '\t{prefix}{aliases} add <role_name>: replace your current color role\n'
        '\t{prefix}{aliases} remove: remove your color role'
    )

    name = 'color'
    category = 'Discord'
    aliases = (name, 'colour')
    bot_perms = (PermissionManageRoles(), )
    guild_only = True
    min_args = 1

    async def on_call(self, ctx, args, **flags):
        if args[1].lower() == 'add':
            if len(args) < 3:
                return await self.on_doc_request(ctx)

            role = await find_role(args[2:], ctx.guild)
            if role is None:
                return await ctx.warn('Role not found on server')

            color_roles = await ctx.bot.pg.fetch(
                "SELECT role_id FROM color_roles WHERE guild_id = $1",
                ctx.guild.id
            )

            color_roles_ids = [r["role_id"] for r in color_roles]

            if role.id not in color_roles_ids:
                return await ctx.warn(f'**{role}** is not a color role You can use `makecolor` command to make it a color role')

            try:
                await ctx.author.remove_roles(
                    *[r for r in ctx.author.roles if r.id in color_roles_ids],
                    reason='color add cleanup'
                )

                await ctx.author.add_roles(role, reason='color add')
            except discord.Forbidden:
                await ctx.error('Unable to assign / remove role. Please, check permissions')

            return await ctx.info(f'Added role **{role}**')
        elif args[1].lower() == 'remove':
            color_roles = await ctx.bot.pg.fetch(
                "SELECT role_id FROM color_roles WHERE guild_id = $1",
                ctx.guild.id
            )

            color_roles_ids = [r["role_id"] for r in color_roles]

            try:
                await ctx.author.remove_roles(
                    *[r for r in ctx.author.roles if r.id in color_roles_ids],
                    reason='color remove'
                )
            except discord.Forbidden:
                await ctx.error('Unable to remove role. Please, check permissions')

            await ctx.info('Removed color role(s)')
        else:
            return await self.on_doc_request(ctx)
