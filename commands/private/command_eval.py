from commands.commandbase import CommandBase

from io import StringIO

import traceback
import sys


class Command(CommandBase):
    """{prefix}{keywords} <code>
    
    Eval python code.
    {protection} or higher permission level required to use"""

    name = 'eval'
    keywords = (name, 'exec')
    arguments_required = 0
    protection = 3

    async def on_call(self, message):
        command = ' '.join(message.content.strip().split(' ')[1:])

        if not command:
            return '❗ Empty command'

        error = ''

        sys.stdout = StringIO()

        try:
            exec(command)
        except:
            error = traceback.format_exc()

        response = sys.stdout.getvalue()

        sys.stdout.close()
        sys.stdout = sys.__stdout__

        if error:
            response += '\nSTDERR: ' + error


        if not response.strip():
            response = 'Evaluated'

        return '```\n' + response + '```'