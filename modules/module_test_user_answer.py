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

    async def on_call(self, msg, *args):
        await self.bot.send_message(
            msg,
            await format_response(
                'Hello, {nick}. Please, send number', msg, self.bot),
            response_to=msg)

        user_answer = await self.bot.wait_for(
            'message', timeout=20,
            check=lambda m: m.content.isdigit() and m.author == msg.author)

        if user_answer is None:
            return 'Answer took too long'

        return 'Ok, you entered `%s`' % user_answer.content