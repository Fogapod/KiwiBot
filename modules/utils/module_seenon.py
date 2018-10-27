from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks
from objects.paginators import Paginator

from utils.funcs import find_user

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [user]'
    short_doc = 'Get list of common guilds with user'

    name = 'seenon'
    aliases = (name, )
    category = 'Discord'
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **flags):
        if len(args) == 1:
            user = ctx.author
        else:
            user = await find_user(args[1:], ctx.message)

        if not user:
            return await ctx.warn('User not found')

        guilds = sorted(
            [g for g in self.bot.guilds if g.get_member(user.id) is not None],
            key=lambda g: (g.member_count, g.name), reverse=True
        )
        if not guilds:
            return await ctx.warn('No common guilds')

        lines = [f'{g.id:<19}| {g.name}' for g in guilds]
        lines_per_chunk = 30
        chunks = [f'```{"id":<19}| name\n{"-" * 53}\n' + '\n'.join(lines[i:i + lines_per_chunk]) + '```' for i in range(0, len(lines), lines_per_chunk)]

        def make_embed(chunk, page=None):
            e = Embed(
                title=f'{len(guilds)} common guilds',
                colour=Colour.gold(),
                description=chunk
            )
            e.set_author(name=user, icon_url=user.avatar_url)

            if page is not None:
                e.set_footer(text=f'Page {i + 1} / {len(chunks)}')

            return e

        p = Paginator(self.bot)
        for i, chunk in enumerate(chunks):
            p.add_page(embed=make_embed(chunk, page=i))

        await p.run(ctx)
