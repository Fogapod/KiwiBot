from modules.modulebase import ModuleBase

from utils.helpers import get_string_after_entry


class Module(ModuleBase):
    """{prefix}{keywords} <text>
    
    Respond with given text.

    {protection} or higher permission level required to use"""

    name = 'say'
    keywords = (name, )
    arguments_required = 1
    protection = 2
    hidden = True

    async def on_call(self, msg, *args, **options):
        await self.bot.send_message(
            msg, get_string_after_entry(args[0], msg.content),
            parse_content=False, response_to=msg
        )