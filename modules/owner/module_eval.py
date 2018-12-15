from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

import io
import sys
import asyncio
import textwrap
import traceback

from contextlib import redirect_stdout

import discord

from utils.formatters import cleanup_code


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <code>'
    short_doc = 'Eval python code'

    name = 'eval'
    aliases = (name, )
    category = 'Owner'
    min_args = 1
    user_perms = (PermissionBotOwner(), )
    hidden = True

    async def on_load(self, from_reload):
        self._last_result = None

    async def on_call(self, ctx, args, **flags):
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
