from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks
from objects.paginators import Paginator

from discord import Embed, Colour


class Module(ModuleBase):

    short_doc = 'Get list of guilds I\'m in'

    name = 'guilds'
    aliases = (name, 'servers')
    category = 'Bot'
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **flags):
        guilds = sorted(
            self.bot.guilds, reverse=True,
            key=lambda g: (g.member_count, g.name)
        )
        lines = [f'{g.id:<19}| {g.name}' for g in guilds]
        lines_per_chunk = 30
        chunks = [f'```{"id":<19}| name\n{"-" * 53}\n' + '\n'.join(lines[i:i + lines_per_chunk]) + '```' for i in range(0, len(lines), lines_per_chunk)]

        p = Paginator(self.bot)
        for i, chunk in enumerate(chunks):
            e = Embed(
                title=f'{len(self.bot.guilds)} guilds',
                colour=Colour.gold(),
                description=chunk
            )
            e.set_footer(text=f'Page {i + 1} / {len(chunks)}')
            p.add_page(embed=e)

        await p.run(ctx)