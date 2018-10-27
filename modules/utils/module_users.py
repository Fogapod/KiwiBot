from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks
from objects.paginators import Paginator

from utils.funcs import find_user

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user>'
    short_doc = 'Get matching users list'

    name = 'users'
    aliases = (name, 'userlist')
    category = 'Discord'
    min_args = 1
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **flags):
        users = await find_user(args[1:], ctx.message, max_count=-1)

        if not users:
            return await ctx.warn('Users not found')

        lines = [f'{u.id:<19}| {u}' for u in users]
        lines_per_chunk = 30
        chunks = [f'```{"id":<19}| name\n{"-" * 53}\n' + '\n'.join(lines[i:i + lines_per_chunk]) + '```' for i in range(0, len(lines), lines_per_chunk)]

        p = Paginator(self.bot)
        for i, chunk in enumerate(chunks):
            e = Embed(
                title=f'Matching users ({len(lines)})',
                colour=Colour.gold(),
                description=chunk
            )
            e.set_footer(text=f'Page {i + 1} / {len(chunks)}')
            p.add_page(embed=e)

        await p.run(ctx)
