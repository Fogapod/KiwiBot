from objects.modulebase import ModuleBase
from objects.permissions import (
    PermissionEmbedLinks, PermissionAddReactions, PermissionReadMessageHistory)
from objects.paginators import Paginator

import random

from discord import Embed, Colour

from utils.funcs import get_local_prefix


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [alias]'
    short_doc = 'Get information about module or category'
    long_doc  = (
        'Subcommands:\n'
        '\t{prefix}{aliases} all:    show help for all commands\n'
        '\t{prefix}{aliases} random: show random command help'
    )

    name = 'help'
    aliases = (name, 'commands')
    category = 'Bot'
    bot_perms = (
        PermissionEmbedLinks(), PermissionAddReactions(),
        PermissionReadMessageHistory()
    )
    flags = {
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
        hidden_flag = flags.get('show-hidden', False)
        hide_normal_flag = flags.get('hide-normal', False)

        if len(args) == 1:
            module_list = []
            for module in self.bot.mm.get_all_modules(hidden=hidden_flag):
                if not module.hidden and hide_normal_flag:
                    continue

                module_list.append(module)

            if not module_list:
                return '{error} No commands found'

            modules_by_category = {}
            for module in module_list:
                category = module.category or 'Uncategorized'
                if category not in modules_by_category:
                    modules_by_category[category] = [module, ]
                else:
                    modules_by_category[category].append(module)

            chunks_by_category = {}
            for category, modules in sorted(modules_by_category.items(), key=lambda x: x[0]):
                lines = sorted([f'**{m.name}**: {m.short_doc}' for m in modules])
                lines_per_chunk = 30
                chunks = [lines[i:i + lines_per_chunk] for i in range(0, len(lines), lines_per_chunk)]
                chunks_by_category[category] = chunks

            local_prefix = await get_local_prefix(ctx)
            total_pages = sum(len(chunks) for chunks in chunks_by_category.values()) + 1

            def make_page(title, chunk, page):
                e = Embed(
                    colour=Colour.gold(), title=title,
                    description='\n'.join(chunk)
                )
                e.set_footer(text=f'Current prefix: {local_prefix}')

                return {
                    'embed': e,
                    'content': f'Page **{page}/{total_pages}** ({len(module_list)}) commands'
                }

            p = Paginator(self.bot)
            p.add_page(**make_page('Categories', [], 1))

            page = 2
            p._pages[0]['embed'].description = 'Category: Pages\n\n'
            for category, chunks in chunks_by_category.items():
                p._pages[0]['embed'].description += f'{category}: **{page:<2}- {page + len(chunks) - 1}**\n'
                for chunk in chunks:
                    p.add_page(**make_page(category, chunk, page))
                    page += 1
            p._pages[0]['embed'].description

            return await p.run(ctx)

        if len(args) > 2:
            return '{warning} help for subcommands is not supported yet'

        if args[1].lower() == 'all':
            category = 'All commands'
            modules = self.bot.mm.get_all_modules(hidden=hidden_flag)
        elif args[1].lower() == 'random':
            return await random.choice(
                self.bot.mm.get_all_modules(hidden=hidden_flag)
            ).on_doc_request(ctx)
        else:
            category = args[1]
            modules = self.bot.mm.get_modules_by_category(category)

        module_list = []
        for module in modules:
            if module.hidden:
                if not (flags.get('show-hidden', False)):
                    continue
            if not module.hidden and flags.get('hide-normal', False):
                continue

            module_list.append(module)

        if module_list:
            lines = sorted([f'**{m.name}**: {m.short_doc}' for m in module_list])
            lines_per_chunk = 30
            chunks = [lines[i:i + lines_per_chunk] for i in range(0, len(lines), lines_per_chunk)]

            p = Paginator(self.bot)
            for i, chunk in enumerate(chunks):
                p.add_page(
                    embed=Embed(
                        colour=Colour.gold(), title=category,
                        description='\n'.join(chunk)
                    ),
                    content=f'Page **{i + 1}/{len(chunks)}** ({len(modules)}) commands'
                )
            await p.run(ctx)
        else:
            module = self.bot.mm.get_module(args[1])

            if not module:
                return '{warning} Unknown command or category'

            return await module.on_doc_request(ctx)
