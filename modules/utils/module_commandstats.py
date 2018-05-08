from objects.modulebase import ModuleBase
from objects.permissions import (
    PermissionEmbedLinks, PermissionAddReactions, PermissionReadMessageHistory)
from objects.paginators import Paginator

from discord import Embed, Colour


class Module(ModuleBase):

    short_doc = 'Show command usage stats'

    name = 'commandstats'
    aliases = (name, 'cmdstats')
    required_perms = (
        PermissionEmbedLinks(), PermissionAddReactions(),
        PermissionReadMessageHistory()
    )

    async def on_call(self, msg, args, **flags):
        keys = await self.bot.redis.keys('command_usage:*')
        usage = await self.bot.redis.mget(*keys)

        lines = [f'{k[14:]:<20}{u}' for k, u in sorted(zip(keys, usage), key=lambda x: int(x[1]), reverse=True)]
        lines_per_chunk = 30
        chunks = [lines[i:i + lines_per_chunk] for i in range(0, len(lines), lines_per_chunk)]

        def make_embed(chunk):
            return Embed(
                colour=Colour.gold(), title='Command usage:',
                description='```\n' + "\n".join(chunk) + '```'
            )

        if len(chunks) == 1:
            return await self.send(msg, embed=make_embed(chunks[0]))

        p = Paginator(self.bot)
        for i, chunk in enumerate(chunks):
            p.add_page(
                embed=make_embed(chunk),
                content=f'Page **{i + 1}/{len(chunks)}**'
            )

        m = await self.send(msg, **p.current_page)
        await p.run(m, target_user=msg.author)