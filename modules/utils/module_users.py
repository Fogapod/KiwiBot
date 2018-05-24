from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks
from objects.paginators import Paginator

from utils.funcs import find_user

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user>'
    short_doc = 'Get matched users list'

    name = 'users'
    aliases = (name, 'userlist')
    category = 'Discord'
    min_args = 1
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **flags):
        users = await find_user(args[1:], ctx.message, max_count=-1)

        if not users:
            return '{warning} Users not found'

        lines = [f'{str(i + 1) + ")":<3}{str(u):<25} {u.id}' for i, u in enumerate(users)]
        lines_per_chunk = 30
        chunks = ['Found users:\n```\n' + '\n'.join(lines[i:i + lines_per_chunk]) + '```' for i in range(0, len(lines), lines_per_chunk)]

        if len(chunks) == 1:
            return await ctx.send(chunks[0])

        p = Paginator(self.bot)
        for i, chunk in enumerate(chunks):
            e = Embed(
                colour=Colour.gold(),
                description=chunk
            )
            e.set_footer(text=f'Page {i + 1} / {len(chunks)}')
            p.add_page(embed=e)

        await p.run(ctx)