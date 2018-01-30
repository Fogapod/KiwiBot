from modules.modulebase import ModuleBase

from utils.formatters import format_response


class Module(ModuleBase):
    """{prefix}{keywords} <code>
    
    Exec terminal command.
    {protection} or higher permission level required to use"""

    name = 'test_user_answer'
    keywords = (name, )
    arguments_required = 0
    protection = 0

    async def on_call(self, message, *args):
        await self.bot.send_message(
            message.channel,
            await format_response(
                'Hello, {nick}. Please, send digit', message, self.bot),
            response_to=message)

        user_answer = await self.bot.wait_for_message(
            timeout=30,
            author=message.author, check=lambda x: x.content.isdigit())

        if user_answer is None:
            return 'Answer took too long'

        return 'Ok, you entered `%s`' % user_answer.content