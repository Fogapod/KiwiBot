from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageRoles

import discord


DEFAULTS = {
    'red':        0xff0000,
    'green':      0x2ecc71,
    'purple':     0x9b59b6,
    'blue':       0x3498db,
    'black':      0x010101,
    'white':      0xffffff,
    'cyan':       0x08f8fc,
    'lime':       0x00ff00,
    'pink':       0xff69b4,
    'yellow':     0xfbf606,
    'darkblue':   0x71368a,
    'darkpurple': 0x71368a,
    'gold':       0xf1c40f
}


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases}'
    short_doc = 'Adds a default list of color roles to the server'

    name = 'makecolors'
    category = 'Discord'
    aliases = (name, 'makecolours')
    bot_perms = (PermissionManageRoles(), )
    user_perms = (PermissionManageRoles(), )
    guild_only = True

    async def on_call(self, ctx, args, **flags):
        existing_names = set(r.name for r in ctx.guild.roles)
        to_create = [name for name in DEFAULTS.keys() if name not in existing_names]

        if not to_create:
            return await ctx.info('Nothing to create, all color roles exist')

        m = await ctx.info(f'Creating {len(to_create)} roles ...')

        for name in to_create:
            created = await ctx.guild.create_role(
                name=name,
                colour=discord.Colour(DEFAULTS[name]),
                reason=f'Makecolors by {ctx.author.id}'
            )

            await created.edit(position=ctx.author.top_role.position - 1)

            await ctx.bot.pg.fetch(
                "INSERT INTO color_roles (guild_id, role_id) VALUES ($1, $2)",
                ctx.guild.id, created.id
            )

        await ctx.bot.edit_message(m, f'Created roles: **{", ".join(to_create)}**')