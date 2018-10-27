from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks
from objects.paginators import Paginator

from utils.funcs import find_user

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [user]'
    short_doc = 'Show list of roles for guild or user'

    name = 'roles'
    aliases = (name, 'listroles')
    category = 'Discord'
    bot_perms = (PermissionEmbedLinks(), )
    guild_only = True

    async def on_call(self, ctx, args, **flags):
        user = None

        if len(args) > 1:
            user = await find_user(args[1:], ctx.message, global_search=False)
            if user is None:
                return await ctx.warn('User not found')
            
            roles = user.roles
        else:
            roles = ctx.guild.roles

        lines = [f'{r.id:<19}| {r.name}' for r in roles[::-1]]
        lines_per_chunk = 30
        chunks = [f'```{"id":<19}| name\n{"-" * 53}\n' + '\n'.join(lines[i:i + lines_per_chunk]) + '```' for i in range(0, len(lines), lines_per_chunk)]

        p = Paginator(self.bot)
        for i, chunk in enumerate(chunks):
            e = Embed(
                title=f'''{'Guild' if user is None else str(user) + "'s"} roles ({len(lines)})''',
                colour=Colour.gold(),
                description=chunk
            )
            e.set_footer(text=f'Page {i + 1} / {len(chunks)}')
            p.add_page(embed=e)

        await p.run(ctx)
