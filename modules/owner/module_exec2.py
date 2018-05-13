from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

from utils.formatters import format_response
from utils.funcs import create_subprocess_shell, execute_process


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <code>'
    short_doc = 'Execute terminal command in a shell'

    name = 'exec2'
    aliases = (name, )
    category = 'Owner'
    min_args = 1
    user_perms = (PermissionBotOwner(), )
    hidden = True

    async def on_call(self, ctx, args, **flags):
        command = args[1:]
        process, pid = await create_subprocess_shell(command)
        
        start_message = await ctx.send(f'Started task with pid `{pid}`')

        stdout, stderr = await execute_process(process, command)
        result = stdout.decode()

        if process.returncode != 0:
            result += '\n' + stderr.decode()

        if not result.strip():
            response = 'Executed'
        else:
            response = await format_response(result, ctx.message, self.bot)

        await self.bot.edit_message(
            start_message, f'```\n{response}```')