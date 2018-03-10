from modules.modulebase import ModuleBase

from permissions import PermissionBotOwner
from utils.formatters import format_response
from utils.helpers import create_subprocess_shell, execute_process, get_string_after_entry


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <code>'
    short_doc = 'Execute terminal command in a shell.'

    name = 'exec2'
    aliases = (name, )
    required_args = 1
    require_perms = (PermissionBotOwner, )
    hidden = True

    async def on_call(self, msg, *args, **options):
        command = get_string_after_entry(args[0], msg.content)
        process, pid = await create_subprocess_shell(command)
        
        start_message = await self.bot.send_message(
            msg, 'Started task with pid `' + str(pid) + '`',
            response_to=msg
        )

        stdout, stderr = await execute_process(process, command)
        result = stdout.decode()

        if process.returncode != 0:
            result += '\n' + stderr.decode()

        if not result.strip():
            response = 'Executed'
        else:
            response = await format_response(result, msg, self.bot)

        await self.bot.edit_message(
            start_message, content='```\n' + response + '```')
