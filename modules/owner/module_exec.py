from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

from utils.funcs import create_subprocess_exec, create_subprocess_shell, execute_process


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <code>'
    short_doc = 'Execute terminal command'
    long_doc = (
        'Command flags:\n'
        '\t[--shell|-s]: run code in shell mode'
    )

    name = 'exec'
    aliases = (name, )
    category = 'Owner'
    min_args = 1
    user_perms = (PermissionBotOwner(), )
    flags = {
        'shell': {
            'alias': 's',
            'bool': True
        }
    }
    hidden = True

    async def on_call(self, ctx, args, **flags):
        try:
            if flags.get('shell', False):
                process, pid = await create_subprocess_shell(args[1:])
            else:
                process, pid = await create_subprocess_exec(*args.args[1:])
        except Exception as e:
            return '{error} Error creating subprocess: ' + str(e)
        
        pid_message = await ctx.send(f'Started process `{pid}`')

        stdout, stderr = await execute_process(process)
        try:
            result = stdout.decode()
        except Exception as e:
            result = f'Error happened while decoding, raw result:\n\n{stdout}'

        if process.returncode != 0:
            result += '\n' + stderr.decode()

        await self.bot.delete_message(pid_message)

        if not result:
            try:
                return await ctx.react('✅', raise_on_errors=True)
            except discord.Forbidden:
                result = 'Executed'

        await ctx.send(f'```\n{result}```')
