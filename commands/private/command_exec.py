from commands.commandbase import CommandBase

from utils.formatters import format_response
from utils.helpers import execute_subprocess

import asyncio
import shlex


class Command(CommandBase):
    """{prefix}{keywords} <code>
    
    Exec terminal command.
    {protection} or higher permission level required to use"""

    name = 'exec'
    keywords = (name, )
    arguments_required = 0
    protection = 2

    async def on_call(self, message):
        command = shlex.split(message.content)[1:]

        couroutine = execute_subprocess(*command, msg=message, bot=self.bot)
        task = self.bot.loop.create_task(couroutine)
        response, eval_message = await task

        if not response.strip():
            response = 'Evaluated'
        else:
            response = await format_response(response, message, self.bot)

        await self.bot.edit_message(eval_message, '```\n' + response + '```')