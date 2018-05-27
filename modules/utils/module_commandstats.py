from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks
from objects.paginators import Paginator

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [command...]'
    short_doc = 'Show command usage stats'

    name = 'commandstats'
    aliases = (name, 'cmdstats')
    category = 'Bot'
    bot_perms = (PermissionEmbedLinks(), )
    flags = {
        'show-disabled': {
            'alias': 'd',
            'bool': True
         },
        'show-hidden': {
            'alias': 'h',
            'bool': True
        },
        'hide-normal': {
            'alias': 'n',
            'bool': True
        }
    }

    async def on_call(self, ctx, args, **flags):
        commands = []
        if len(args) > 1:
            keys = [m.name for m in [self.bot.mm.get_module(n) for n in set(args.args[1:])] if m is not None]
            if keys:
                usage = await self.bot.redis.mget(*[f'command_usage:{k}' for k in keys])
                commands = tuple(zip(keys, [int(u) for u in usage]))
        else:
            keys = await self.bot.redis.keys('command_usage:*')
            usage = await self.bot.redis.mget(*keys)

            for k, u in zip(keys, usage):
                name = k[14:]
                module = self.bot.mm.get_module(name)
                if module:
                    if module.disabled:
                        if not (flags.get('show-disabled', False)):
                            continue
                    if module.hidden:
                        if not (flags.get('show-hidden', False)):
                            continue
                    if not (module.disabled or module.hidden) and flags.get('hide-normal', False):
                        continue
                    commands.append((name, int(u)))

        if not commands:
            return '{error} No commands found'

        total_usage = sum(u for c, u in commands)
        lines = [f'{c:<20}{u}' for c, u in sorted(commands, key=lambda x: int(x[1]), reverse=True)]
        lines_per_chunk = 30
        chunks = [lines[i:i + lines_per_chunk] for i in range(0, len(lines), lines_per_chunk)]

        def make_embed(chunk):
            e = Embed(
                colour=Colour.gold(), title='Command usage:',
                description='```\n' + "\n".join(chunk) + '```'
            )
            e.set_footer(
                text=f'Commands used in total: {total_usage}',
                icon_url=self.bot.user.avatar_url
            )
            return e

        p = Paginator(self.bot)
        for i, chunk in enumerate(chunks):
            p.add_page(
                embed=make_embed(chunk),
                content=f'Page **{i + 1}/{len(chunks)}**'
            )

        await p.run(ctx)