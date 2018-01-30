from modules.modulebase import ModuleBase

from utils.constants import STOP_EXIT_CODE


class Module(ModuleBase):
    """{prefix}{keywords} <exit_code>*
    
    Stop bot.
    {protection} or higher permission level required to use"""

    name = 'stop'
    keywords = (name, 'die')
    protection = 2

    async def on_call(self, message, *args):
        await self.bot.add_reaction(message, '✅')
        exit_code = args[1] if len(args) == 2 else STOP_EXIT_CODE
        await self.bot.stop(exit_code)