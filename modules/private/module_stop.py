from modules.modulebase import ModuleBase

from utils.constants import STOP_EXIT_CODE


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [exit_code]'
    short_doc = 'Stop bot.'

    name = 'stop'
    aliases = (name, 'die', '!')
    protection = 2
    hidden = True

    async def on_call(self, message, *args, **options):
        await message.add_reaction('✅')
        exit_code = args[1] if len(args) == 2 else STOP_EXIT_CODE
        self.bot.stop(exit_code)