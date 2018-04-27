from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks, PermissionAddReactions
from objects.paginators import Paginator

from utils.funcs import find_user

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [user]'
    short_doc = 'Get list of common guilds with user.'

    name = 'seenon'
    aliases = (name, )
    required_perms = (PermissionEmbedLinks(), PermissionAddReactions())

    async def on_call(self, msg, args, **flags):
        if len(args) == 1:
            user = msg.author
        else:
            user = await find_user(args[1:], msg, self.bot)

        if not user:
            return '{warning} User not found'

        guilds = [g for g in self.bot.guilds if g.get_member(user.id) is not None]
        lines = [f'{str(i + 1) + ")":<3}{g.name}' for i, g in enumerate(guilds)]
        lines_per_chunk = 20
        chunks = ['```\n' + '\n'.join(lines[i:i + lines_per_chunk]) + '```' for i in range(0, len(lines), lines_per_chunk)]

        def make_embed(chunk, page=None):
            e = Embed(
                title='Common guilds',
                colour=Colour.gold(),
                description=chunk
            )
            e.set_author(name=user, icon_url=user.avatar_url)

            if page:
                e.set_footer(text=f'Page {i + 1} / {len(chunks)}')

            return e

        if len(chunks) == 1:
            return await self.send(msg, embed=make_embed(chunks[0]))

        p = Paginator(self.bot)
        for i, chunk in enumerate(chunks):
            p.add_page(embed=make_embed(chunk, page=i))

        m = await self.send(msg, **p.current_page)
        await p.run(m, target_user=msg.author)