from objects.modulebase import ModuleBase
from objects.permissions import (
    PermissionEmbedLinks, PermissionAddReactions, PermissionReadMessageHistory)
from objects.paginators import Paginator

from discord import Embed, Colour


class Module(ModuleBase):

    short_doc = 'Get list of guilds I\'m in'

    name = 'guilds'
    aliases = (name, 'servers')
    category = 'Bot'
    bot_perms = (
        PermissionEmbedLinks(), PermissionAddReactions(),
        PermissionReadMessageHistory()
    )

    async def on_call(self, msg, args, **flags):
        guilds = sorted(
            self.bot.guilds, reverse=True,
            key=lambda g: (g.member_count, g.name)
        )
        lines = [f'{str(i + 1) + ")":<3}{g.name:<25} {g.id}' for i, g in enumerate(guilds)]
        lines_per_chunk = 30
        chunks = ['```\n' + '\n'.join(lines[i:i + lines_per_chunk]) + '```' for i in range(0, len(lines), lines_per_chunk)]

        if len(chunks) == 1:
            return await self.send(msg, content=chunks[0])

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