from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks
from objects.paginators import Paginator

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases}'
    short_doc = 'Get list of colors available for assigment'

    name = 'colors'
    aliases = (name, 'colours')
    category = 'Discord'
    bot_perms = (PermissionEmbedLinks(), )
    guild_only = True

    async def on_call(self, ctx, args, **flags):
        colors = await ctx.bot.pg.fetch(
            "SELECT role_id FROM color_roles WHERE guild_id = $1",
            ctx.guild.id
        )

        guild_roles = []
        missing_roles = []

        for c in colors:
            r = ctx.guild.get_role(c['role_id'])

            if r is None:
                missing_roles.append(c['role_id'])
            else:
                guild_roles.append(r)

        if missing_roles:
            await ctx.bot.pg.fetch(
                "DELETE FROM color_roles WHERE guild_id = $1 AND role_id = ANY($2)",
                ctx.guild.id, missing_roles
            )

        if not guild_roles:
            return await ctx.info('No color roles')

        guild_roles.sort(key=lambda x: x.position, reverse=True)

        lines = [f'{r.color} | {r.name}' for r in guild_roles]
        lines_per_chunk = 30
        chunks = [f'```  color | role name\n{"-" * 53}\n' + '\n'.join(lines[i:i + lines_per_chunk]) + '```' for i in range(0, len(lines), lines_per_chunk)]

        p = Paginator(self.bot)
        for i, chunk in enumerate(chunks):
            e = Embed(
                title=f'Available colors ({len(lines)})',
                colour=Colour.gold(),
                description=chunk
            )
            e.set_footer(text=f'Page {i + 1} / {len(chunks)}')
            p.add_page(embed=e)

        await p.run(ctx)
