from objects.modulebase import ModuleBase

import io
import sys
import asyncio
import textwrap
import traceback

from constants import BOT_OWNER_ID

from contextlib import redirect_stdout

import discord

from utils.formatters import cleanup_code


fake_data = '''
class HTTP:
    token = "MA==.ekU5.CZ7eHwhU97J0uKeDMOuaQQdeaUM"

    def __repr__(self):
        return "<discord.http.HTTPClient object at 0x7f8b77633da0>"

class Bot:
    def __init__(self):
        self.http = HTTP()

    def __repr__(self):
        return "<objects.bot.KiwiBot object at 0x7f8b7bf06c50>"

bot = Bot()
'''

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <code>'
    short_doc = 'Eval python code'

    name = 'eval'
    aliases = (name, )
    category = 'Owner'
    min_args = 1
    hidden = True

    async def on_load(self, from_reload):
        self._last_result = None

    async def on_call(self, ctx, args, **flags):
        program, _ = cleanup_code(args[1:])

        if ctx.message.author.id == BOT_OWNER_ID:
            program, _ = cleanup_code(args[1:])

            glob = {
                'self': self,
                'bot': self.bot,
                'ctx': ctx,
                'msg': ctx.message,
                'guild': ctx.guild,
                'author': ctx.author,
                'channel': ctx.channel,
                'discord': discord,
                '_': self._last_result
            }

            fake_stdout = io.StringIO()

            to_compile = 'async def func():\n' + textwrap.indent(program, '  ')

            try:
                exec(to_compile, glob)
            except Exception as e:
                return f'```py\n{e.__class__.__name__}: {e}\n```'

            func = glob['func']

            try:
                with redirect_stdout(fake_stdout):
                    returned = await func()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                return f'```py\n{fake_stdout.getvalue()}{traceback.format_exc()}\n```'
            else:
                from_stdout = fake_stdout.getvalue()

                if returned is None:
                    if from_stdout:
                        return f'```py\n{from_stdout}\n```'
                    try:
                        await ctx.react('✅')
                    except discord.Forbidden:
                        return 'Evaluated'
                else:
                    self._last_result = returned
                    return f'```py\n{from_stdout}{returned}```'
        else:
            params = {
                'LanguageChoice': 24,
                'Program':        f"{fake_data}{program}",
                'CompilerArgs':   ""
            }

            result = ""

            async with self.bot.sess.post("https://rextester.com/rundotnet/api", params=params) as r:
                if r.status == 200:
                    result_json = await r.json()
                    result  = result_json['Result'] or ''
                    if result_json['Errors']:
                        error_lines = result_json['Errors'].split('\n')
                        result += f"""
Traceback (most recent call last):
  File "/home/kiwi/KiwiBot/modules/owner/module_eval.py", line 80, in on_call
    returned = await func()
  File "<string>", line 2, in func
{error_lines[-2] if len(error_lines) > 1 else error_lines[0]}"""
                else:
                    return await ctx.error('Error. Please, try again later')

            if not result or result == '\n':
                result = 'Empty output'

            return f'```python\n{result}```'
