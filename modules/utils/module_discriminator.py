from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks
from objects.paginators import Paginator

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [discriminator]'
    short_doc = 'Get list of users with given discriminator'

    name = 'discriminator'
    aliases = (name, 'discrim')
    category = 'Discord'
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **flags):
        if len(args) == 1:
            discrim = ctx.author.discriminator
        else:
            if args[1].isdigit() and len(args[1]) == 4:
                discrim = args[1]
            else:
                return '{warning} Invalid discriminator given'

        matched = []
        for user in self.bot.users:
            if user.discriminator == discrim and not user.bot and user != ctx.author:
                matched.append(user)

        if not matched:
            return '{warning} Users with discriminator **%s** not found' % discrim

        lines = sorted([str(u) for u in matched], key=lambda s: (len(s), s))
        users_per_chunk = 30
        chunks = [lines[i:i + users_per_chunk] for i in range(0, len(lines), users_per_chunk)]

        if len(chunks) == 1:
            return await ctx.send('```\n' + '\n'.join(chunks[0]) + '```')

        p = Paginator(self.bot)
        for i, chunk in enumerate(chunks):
            e = Embed(description=f'```\n' + '\n'.join(chunk) + '```', colour=Colour.gold())
            e.set_footer(text=f'Page {i + 1}/{len(chunks)} ({len(lines)}) results')
            p.add_page(embed=e)

        await p.run(ctx)