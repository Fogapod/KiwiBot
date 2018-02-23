from modules.modulebase import ModuleBase

from utils.formatters import format_response
from utils.helpers import create_subprocess_exec, execute_process, get_string_after_entry


class Module(ModuleBase):
    """{prefix}{keywords} <code>
    
    Exec terminal command.
    {protection} or higher permission level required to use"""

    name = 'exec'
    keywords = (name, )
    arguments_required = 1
    protection = 2
    hidden = True

    async def on_call(self, msg, *args, **options):
        command = get_string_after_entry(args[0], msg.content).split(' ')
        process, pid = await create_subprocess_exec(*command)
        
        start_message = await self.bot.send_message(
            msg, 'Started task with pid `' + str(pid) + '`',
            response_to=msg
        )

        stdout, stderr = await execute_process(process, command)
        result = stdout.decode().strip()

        if process.returncode != 0:
            result += '\n' + stderr.decode()

        if not result.strip():
            response = 'Executed'
        else:
            response = await format_response(result, msg, self.bot)

        await self.bot.edit_message(
            start_message, content='```\n' + response + '```')