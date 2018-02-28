from modules.modulebase import ModuleBase

from utils.helpers import get_string_after_entry

import io
import sys
import asyncio
import traceback

import textwrap
from contextlib import redirect_stdout


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <code>'
    short_doc = 'Eval python code.'

    name = 'eval'
    aliases = (name, )
    arguments_required = 1
    protection = 2
    hidden = True

    async def on_load(self, from_reload):
        self._last_result = None

    async def on_call(self, msg, *args, **options):
        program = get_string_after_entry(args[0], msg.content)

        glob = {
            'self': self,
            'bot': self.bot,
            'msg': msg,
            'message': msg,
            '_': self._last_result
        }

        glob.update(globals())

        fake_stdout = io.StringIO()

        to_compile = 'async def func():\n' + textwrap.indent(program, '  ')

        try:
            exec(to_compile, glob)
        except Exception as e:
            return '```py\n%s: %s\n```' % (e.__class__.__name__, e)

        func = glob['func']

        try:
            with redirect_stdout(fake_stdout):
                result = await func()
        except Exception as e:
            output = fake_stdout.getvalue()
            return '```py\n%s%s\n```' %(output, traceback.format_exc())
        else:
            output = fake_stdout.getvalue()

            if result is None:
                if output:
                    return '```py\n%s\n```' % output
            else:
                self._last_result = result

            return '```py\n%s%s\n```' % (output, result if result is not None else 'Evaluated')