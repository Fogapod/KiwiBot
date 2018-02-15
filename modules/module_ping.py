from modules.modulebase import ModuleBase

from utils.helpers import create_subprocess_exec, execute_process


class Module(ModuleBase):
    """{prefix}{keywords} <url>*
    
    Get bot response time / ping url.
    {protection} or higher permission level required to use"""

    name = 'ping'
    keywords = (name, )
    arguments_required = 0
    protection = 0

    async def on_call(self, msg, *args):
        ping_msg = await self.bot.send_message(
            msg, 'Pinging ...', response_to=msg)

        if len(args) == 2:
            program = ['ping', '-c', '4', args[1]]
            process, pid = await create_subprocess_exec(*program)
            stdout, stderr = await execute_process(process, program)

            await self.bot.edit_message(
                ping_msg,
                content='```\n' + (stdout.decode() or stderr.decode()) + '```'
            )
            return

        msg_timestamp = msg.edited_at if msg.edited_at else msg.created_at
        delta = int(round((ping_msg.created_at.timestamp() - msg_timestamp.timestamp()) * 1000))

        result = 'Pong, it took `' + str(delta) + 'ms`'

        args = msg.content.strip().split(' ')
        result += ' to ping `' + ' '.join(args[1:]) + '`' if args[1:] else 'to respond'

        await self.bot.edit_message(ping_msg, content=result)