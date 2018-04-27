from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks, PermissionAddReactions
from objects.paginators import Paginator

from discord import Embed, Colour


class Module(ModuleBase):

    short_doc = 'Get list of guilds I\'m in.'

    name = 'guilds'
    aliases = (name, 'servers')
    required_perms = (PermissionEmbedLinks(), PermissionAddReactions())

    async def on_call(self, msg, args, **flags):
        lines = [f'{str(i + 1) + ")":<3}{g.name:<25} {g.id}' for i, g in enumerate(self.bot.guilds)]
        lines_per_chunk = 20
        chunks = ['```\n' + '\n'.join(lines[i:i + lines_per_chunk]) + '```' for i in range(0, len(lines), lines_per_chunk)]

        if len(chunks) == 1:
            await self.send(msg, content=chunks[0])
            return

        p = Paginator(self.bot)
        for i, chunk in enumerate(chunks):
            e = Embed(
                title=f'{len(self.bot.guilds)} guilds',
                colour=Colour.gold(),
                description=chunk
            )
            e.set_footer(text=f'Page {i + 1} / {len(chunks)}')
            p.add_page(embed=e)

        m = await self.send(msg, **p.current_page)
        await p.run(m, target_user=msg.author)