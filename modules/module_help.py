from modules.modulebase import ModuleBase

from utils.helpers import get_local_prefix


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [alias]'
    short_doc = 'Get information about bot or module (if given).'

    name = 'help'
    aliases = (name, )
    arguments_required = 0
    protection = 0

    async def on_call(self, msg, *args, **flags):
        if len(args) == 1:
            module_list = []
            for name, module in self.bot.mm.modules.items():
                if not (module.hidden or module.disabled):
                    module_list.append(name)

            return (
                'Current prefix: ' + await get_local_prefix(msg, self.bot) + '\n'
                'Available commands are: `%s`' % ', '.join(module_list)
            )

        if len(args) > 2:
            return '{warning} help for subcommands is not supported yet'

        module = self.bot.mm.get_module(args[1].lower())

        if not module or module.disabled:
            return '{warning} Command `' + args[1] + '` not found'

        return await module.on_doc_request(msg)