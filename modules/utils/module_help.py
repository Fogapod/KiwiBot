from objects.modulebase import ModuleBase
from objects.permissions import (
    PermissionEmbedLinks, PermissionAddReactions, PermissionReadMessageHistory)
from objects.paginators import Paginator

from utils.funcs import get_local_prefix

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [alias]'
    short_doc = 'Get information about bot or module (if given)'

    name = 'help'
    aliases = (name, 'commands')
    bot_perms = (
        PermissionEmbedLinks(), PermissionAddReactions(),
        PermissionReadMessageHistory()
    )
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

    async def on_call(self, msg, args, **flags):
        if len(args) == 1:
            module_list = []
            for name, module in self.bot.mm.modules.items():
                if module.disabled:
                    if not (flags.get('show-disabled', False)):
                        continue
                if module.hidden:
                    if not (flags.get('show-hidden', False)):
                        continue
                if not (module.disabled or module.hidden) and flags.get('hide-normal', False):
                    continue

                module_list.append((name, module))

            if not module_list:
                return '{error} No commands found'

            lines = sorted([f'{m.name:<20}{m.short_doc}' for n, m in module_list])
            lines_per_chunk = 30
            chunks = [lines[i:i + lines_per_chunk] for i in range(0, len(lines), lines_per_chunk)]

            local_prefix = await get_local_prefix(msg, self.bot)

            def make_embed(chunk):
                e = Embed(
                    colour=Colour.gold(), title='Available commands:',
                    description='```\n' + "\n".join(chunk) + '```'
                )
                e.set_footer(text=f'Current prefix: {local_prefix}')
                return e

            if len(chunks) == 1:
                return await self.send(
                    msg, f'{len(lines)} commands', embed=make_embed(chunks[0]))

            p = Paginator(self.bot)
            for i, chunk in enumerate(chunks):
                p.add_page(
                    embed=make_embed(chunk),
                    content=f'Page **{i + 1}/{len(chunks)}** ({len(lines)}) commands'
                )

            m = await self.send(msg, **p.current_page)
            return await p.run(m, target_user=msg.author)

        if len(args) > 2:
            return '{warning} help for subcommands is not supported yet'

        module = self.bot.mm.get_module(args[1].lower())

        if not module or module.disabled:
            return '{warning} Command `' + args[1] + '` not found'

        return await module.on_doc_request(msg)