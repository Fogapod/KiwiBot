from commands.commandbase import CommandBase

import io
import sys
import asyncio
import traceback


class Command(CommandBase):
    """{prefix}{keywords} <code>
    
    Eval python code.
    {protection} or higher permission level required to use"""

    name = 'eval'
    keywords = (name, )
    arguments_required = 0
    protection = 2

    async def on_call(self, message):
        program = ' '.join(message.content.strip().split(' ')[1:])
        
        result = await self.bot.loop.run_in_executor(
            None, self.exec_code, program, message)

        return '```\n' + (result if result else 'Evaluated') + '```'

    def exec_code(self, code, message):
        try:
            sys.stdout = fake_stdout = io.StringIO()

            try:
                exec(code)
            except:
                tb = traceback.format_exc()
            else:
                tb = ''

            stdout_text = fake_stdout.getvalue()

            response = stdout_text

            if tb:
                response += '\n' + tb

            sys.stdout.close()

        finally:
            sys.stdout = sys.__stdout__

        return response