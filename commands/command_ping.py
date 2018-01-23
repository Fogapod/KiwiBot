from commands.commandbase import CommandBase

import time


class Command(CommandBase):
    """{prefix}{keywords}
    
    Get bot response time.
    {protection} or higher permission level required to use"""

    name = 'ping'
    keywords = (name, )
    arguments_required = 0
    protection = 0

    async def on_call(self, message):
        start_time = time.time()

        ping_message = await self.bot.send_message(
            message.channel, 'Pinging ...')

        delta = int(round((time.time() - start_time) * 1000))
        result = 'Pong, it took `' + str(delta) + 'ms`'

        args = message.content.strip().split(' ')
        result += ' to ping `' + ' '.join(args[1:]) + '`' if args[1:] else ''

        await self.bot.edit_message(ping_message, result)