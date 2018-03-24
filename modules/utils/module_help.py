from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks, PermissionAddReactions
from objects.paginators import Paginator

from utils.funcs import get_local_prefix

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [alias]'
    short_doc = 'Get information about bot or module (if given).'

    name = 'help'
    aliases = (name, 'commands')
    required_perms = (PermissionEmbedLinks, PermissionAddReactions)

    async def on_call(self, msg, *args, **flags):
        # temporary solution
        args = list(args)
        if '-d' in args:
            args.remove('-d')
            flags['show-disabled'] = True
        if '--show-disabled' in args:
            args.remove('--show-disabled')
            flags['show-disabled'] = True
        if '-h' in args:
            args.remove('-h')
            flags['show-hidden'] = True
        if '--show-hidden' in args:
            args.remove('--show-hidden')
            flags['show-hidden'] = True

        if len(args) == 1:
            module_list = []
            for name, module in self.bot.mm.modules.items():
                if module.disabled:
                    if not flags.get('show-disabled', False):
                        continue
                if module.hidden:
                    if not flags.get('show-hidden', False):
                        continue

                module_list.append((name, module))

            lines = sorted([f'{m.name:<20}{m.short_doc}' for n, m in module_list])
            lines_per_chunk = 20
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
                await self.send(msg, embed=make_embed(chunks[0]))
                return

            p = Paginator(self.bot)
            for i, chunk in enumerate(chunks):
                p.add_page(embed=make_embed(chunk), content=f'Help page **{i + 1}/{len(chunks)}**')

            m = await self.send(msg, **p.current_page)
            await p.run_paginator(m, msg.author)
            return

        if len(args) > 2:
            return '{warning} help for subcommands is not supported yet'

        module = self.bot.mm.get_module(args[1].lower())

        if not module or module.disabled:
            return '{warning} Command `' + args[1] + '` not found'

        return await module.on_doc_request(msg)