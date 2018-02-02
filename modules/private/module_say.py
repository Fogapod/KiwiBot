from modules.modulebase import ModuleBase


class Module(ModuleBase):
    """{prefix}{keywords} <text>
    
    Respomd with given text.

    {protection} or higher permission level required to use"""

    name = 'say'
    keywords = (name, )
    arguments_required = 1
    protection = 2

    async def on_call(self, message, *args):
        await self.bot.send_message(
            message, message.content[len(args[0]):].strip(),
            parse_content=False
        )