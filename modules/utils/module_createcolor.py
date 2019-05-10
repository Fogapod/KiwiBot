from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageRoles

from discord import Colour

from PIL import ImageColor


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <color> [name]'
    short_doc = 'Creates color role with given color'

    name = 'createcolor'
    aliases = (name, 'createcolour')
    category = 'Discord'
    bot_perms = (PermissionManageRoles(), )
    user_perms = (PermissionManageRoles(), )
    min_args = 1

    async def on_call(self, ctx, args, **flags):
        try:
            rgb = ImageColor.getrgb(args[1])
            color = Colour.from_rgb(*rgb)
        except ValueError as e:
            return await ctx.warn('Not a valid colour')

        if len(args) > 2:
            name = args[2:]
        else:
            name = args[1]

        if len(name) > 100:
            return await ctx.error('Role name should be 100 or fewer symbols')

        created = await ctx.guild.create_role(
            name=name, colour=color, reason=f'Createcolor by {ctx.author.id}'
        )

        await created.edit(position=ctx.author.top_role.position - 1)

        await ctx.bot.pg.fetch(
            "INSERT INTO color_roles (guild_id, role_id) VALUES ($1, $2)",
            ctx.guild.id, created.id
        )

        await ctx.info(f'Created role **{created}**')
