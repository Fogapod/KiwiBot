from modules.modulebase import ModuleBase

import asyncio


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
            msg.channel, 'Pinging ...', response_to=msg)

        if len(args) == 2:
            process, pid = await self.create_subprocess_exec(*['ping', '-c', '4', args[1]])
            stdout, stderr = await process.communicate()
            await self.bot.edit_message(
                ping_msg,
                '```\n' + (stdout.decode() or stderr.decode()) + '```'
            )
            return

        msg_timestamp = msg.edited_timestamp if msg.edited_timestamp else msg.timestamp
        delta = int(round((ping_msg.timestamp.timestamp() - msg_timestamp.timestamp()) * 1000))

        result = 'Pong, it took `' + str(delta) + 'ms`'

        args = msg.content.strip().split(' ')
        result += ' to ping `' + ' '.join(args[1:]) + '`' if args[1:] else ''

        await self.bot.edit_message(ping_msg, result)
        
    async def create_subprocess_exec(self, *args):
        process = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE,
                   stderr=asyncio.subprocess.PIPE
        )
        return process, str(process.pid)