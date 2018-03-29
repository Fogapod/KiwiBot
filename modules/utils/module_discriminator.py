from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks, PermissionAddReactions
from objects.paginators import Paginator

from discord import Embed


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [discriminator]'
    short_doc = 'Get list of users with given discriminator.'

    name = 'discriminator'
    aliases = (name, 'discrim')
    required_perms = (PermissionEmbedLinks, PermissionAddReactions)

    async def on_call(self, msg, *args, **flags):
        if len(args) == 1:
            discrim = msg.author.discriminator
        else:
            if args[1].isdigit() and len(args[1]) == 4:
                discrim = args[1]
            else:
                return '{warning} Invalid discriminator given'

        matched = []
        for user in self.bot.users:
            if user.discriminator == discrim and not user.bot and user != msg.author:
                matched.append(user)

        if not matched:
            return '{warning} Users with discriminator **%s** not found' % discrim

        lines = sorted([str(u) for u in matched], key=lambda s: (len(s), s))
        users_per_chunk = 25
        chunks = [lines[i:i + users_per_chunk] for i in range(0, len(lines), users_per_chunk)]

        if len(chunks) == 1:
            await self.send(msg, content='```\n' + '\n'.join(chunks[0]) + '```')
            return

        p = Paginator(self.bot)
        for i, chunk in enumerate(chunks):
            e = Embed(description=f'```\n' + '\n'.join(chunk) + '```')
            e.set_footer(text=f'Page {i + 1}/{len(chunks)}')
            p.add_page(embed=e)

        m = await self.send(msg, **p.current_page)
        await p.run(m, target_user=msg.author)