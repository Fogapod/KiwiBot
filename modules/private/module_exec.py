from modules.modulebase import ModuleBase

from utils.formatters import format_response

import asyncio
import shlex


class Module(ModuleBase):
    """{prefix}{keywords} <code>
    
    Exec terminal command.
    {protection} or higher permission level required to use"""

    name = 'exec'
    keywords = (name, 'exec2')
    arguments_required = 0
    protection = 2

    async def on_call(self, message, *args):
        if args[0].lower() == 'exec2':
            command = ' '.join(args[1:])
            process, pid = await self.create_subprocess_shell(command)
        else:
            command = shlex.split(message.content)[1:]
            process, pid = await self.create_subprocess_exec(*command)
        
        start_message = await self.bot.send_message(
            message.channel, 'Started task with pid `' + pid + '`',
            response_to=message
        )

        print('Started  task:', command, '(pid = ' + pid + ')')
        stdout, stderr = await process.communicate()
        print('Finiahed task:', command, '(pid = ' + pid + ')')

        result = stdout.decode().strip()

        if process.returncode != 0:
            result += '\n' + stderr.decode()

        if not result.strip():
            response = 'Executed'
        else:
            response = await format_response(result, message, self.bot)

        await self.bot.edit_message(start_message, '```\n' + response + '```')

    async def create_subprocess_shell(self, program):
        process = await asyncio.create_subprocess_shell(
	        program, stdout=asyncio.subprocess.PIPE,
                     stderr=asyncio.subprocess.PIPE
        )
        return process, str(process.pid)

    async def create_subprocess_exec(self, *args):
        process = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE,
                   stderr=asyncio.subprocess.PIPE
        )
        return process, str(process.pid)