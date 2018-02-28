from modules.modulebase import ModuleBase

from utils.constants import ACCESS_LEVEL_NAMES


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [alias]'
    short_doc = 'Get information about bot or module (if given).'

    name = 'help'
    aliases = (name, )
    arguments_required = 0
    protection = 0

    async def on_call(self, message, *args, **options):
        if len(args) == 1:
            module_list = []
            for name, module in self.bot.mm.modules.items():
                if not (module.hidden or module.disabled):
                    module_list.append(name)

            return 'Available commands are: `%s`' % ', '.join(module_list)

        if len(args) > 2:
            return '{warning} help for subcommands is not supported yet'

        module = self.bot.mm.get_module(args[1].lower())

        if not module or module.disabled:
            return 'Command `' + args[1] + '` not found'

        help_text = await module.on_doc_request()

        if help_text is not None:
            return help_text

        help_text = ''
        help_text += f'{module.usage_doc}'          if module.usage_doc else ''
        help_text += f'\n\n{module.short_doc}'      if module.short_doc else ''
        help_text += f'\n\n{module.additional_doc}' if module.additional_doc else ''
        help_text += f'\n\n{module.permission_doc}' if module.permission_doc else ''

        help_text = help_text.strip()

        return await self.format_help(help_text, module)

    async def format_help(self, help_text, command):
        help_text = help_text.replace('\n    ', '\n')
        help_text = help_text.replace('{prefix}', self.bot.prefixes[0])

        if len(command.aliases) == 1:
            help_text = help_text.replace('{aliases}', command.aliases[0])
        else:
            help_text = help_text.replace('{aliases}', '[' + '|'.join(command.aliases) + ']')

        help_text = help_text.replace('{protection}', ACCESS_LEVEL_NAMES[command.protection])

        return '```\n' + help_text + '```'