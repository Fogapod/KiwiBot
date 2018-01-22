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
        delta = time.time() - time.mktime(message.timestamp.timetuple())
        result = 'Pong, it took `' + str(int(round(delta / 1000))) + 'ms`'
        args = message.content.strip().split(' ')
        result += ' to ping `' + ' '.join(args[1:]) + '`' if args[1:] else ''
        return result