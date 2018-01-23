from commands.commandbase import CommandBase

from utils.formatters import format_response

import asyncio


class Command(CommandBase):
    """{prefix}{keywords} <code>
    
    Eval python code.
    {protection} or higher permission level required to use"""

    name = 'eval'
    keywords = (name, 'exec')
    arguments_required = 0
    protection = 2

    async def on_call(self, message):
        program = ' '.join(message.content.strip().split(' ')[1:])
        command = ['python', '-c', program]

        couroutine = self.run_command(message, *command)
        task = self.bot.loop.create_task(couroutine)
        response, eval_message = await task

        if not response.strip():
            response = 'Evaluated'
        else:
            response = await format_response(response, message, self.bot)

        await self.bot.edit_message(eval_message, '```\n' + response + '```')

        return 


    async def run_command(self, message, *args):
        process = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE,
                   stderr=asyncio.subprocess.PIPE
        )

        print('Started task:', args, '(pid = ' + str(process.pid) + ')')
        eval_message = await self.bot.send_message(
            message.channel, 'Started task with pid `' + str(process.pid) + '`')

        stdout, stderr = await process.communicate()

        print('Completed:', args, '(pid = ' + str(process.pid) + ')')

        result = stdout.decode().strip()

        if process.returncode != 0:
            result += '\n' + stderr.decode()

        return result, eval_message