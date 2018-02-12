from modules.modulebase import ModuleBase

from utils.constants import ACCESS_LEVEL_NAMES

import random


class Module(ModuleBase):
    """{prefix}{keywords} <module>*
    
    Get information about bot or module if provided.
    {protection} or higher permission level required to use"""

    name = 'help'
    keywords = (name, )
    arguments_required = 0
    protection = 0

    async def on_call(self, message, *args):
        if len(args) == 1:
            module_list = []
            for name, module in self.bot.mm.modules.items():
                if not module.hidden:
                    module_list.append(name)

            return 'Available modules are: `%s`' % ', '.join(module_list)

        module = None

        if len(args) > 2:
            return '{warning} help for subcommands is not supported yet'

        for k, v in self.bot.mm.modules.items():
            if args[1] in v.keywords:
                module = v
                break

        if not module:
            return 'Module `' + args[1] + '` not found'

        help_text = await module.on_doc_request()

        if help_text is not None:
            return help_text

        return await self.format_help(module.__doc__, module)

    async def format_help(self, help_text, command):
        help_text = help_text.replace('\n    ', '\n')
        help_text = help_text.replace('{prefix}', random.choice(self.bot.prefixes[:-2]))

        if len(command.keywords) == 1:
            help_text = help_text.replace('{keywords}', command.keywords[0])
        else:
            help_text = help_text.replace('{keywords}', '[' + '|'.join(command.keywords) + ']')

        help_text = help_text.replace('{protection}', ACCESS_LEVEL_NAMES[command.protection])

        return '```\n' + help_text + '```'