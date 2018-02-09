import traceback
import asyncio
import time
import sys

import discord

from modulemanager import ModuleManager

from utils.constants import PREFIXES, STOP_EXIT_CODE
from utils.formatters import format_response, trim_message
from utils.config import Config


class BotMyBot(discord.Client):

    def __init__(self, *args, **kwargs):
        super(BotMyBot, self).__init__(*args, **kwargs)
        self.start_time = 0

        self.config = Config('config.json', loop=self.loop)
        self.token = self.config['token']

        self.tracked_messages = {}
        self.mm = ModuleManager(self)

    def run(self, token=None):
        if token is None:
            token = self.token
        else:
            self.token = token

        super(BotMyBot, self).run(token, reconnect=True)

    def restart(self):
        self.stop(0)

    def stop(self, exit_code=STOP_EXIT_CODE):
        self.loop.stop()
        sys.exit(exit_code)

    async def on_ready(self):
        await self.mm.load_modules()
        print('Loaded modules: [%s]' % ' '.join(self.mm.modules.keys()))
        self.start_time = time.time()
        print('Ready')

    async def close(self):
        await super(BotMyBot, self).close()
        await self.mm.unload_modules()
        print('Closed')

    async def on_message(self, message, from_edit=False):
        if message.author.bot:
            return

        if message.guild is None:
            await self.send_message(
                message.channel, 'Personal messages are not supported yet')

        if not from_edit:
            await self.track_message(message)

        lower_content = message.content.lower()

        if not lower_content.startswith(PREFIXES):
            return

        message.content = message.content[
            len(next(p for p in PREFIXES if lower_content.startswith(p))):].strip()
        
        if not message.content:
            return

        module_response = await self.mm.check_modules(message)

        if module_response:
            module_response = await format_response(
                module_response, message, self)

        if module_response:
            await self.send_message(
                message, module_response, response_to=message)

    async def on_message_edit(self, before, after):
        if before.content == after.content:
            return

        if before.id in self.tracked_messages:
            if self.tracked_messages[before.id] is not None:
                await self.delete_message(self.tracked_messages[before.id])
                self.tracked_messages[before.id] = None

            await self.on_message(after, from_edit=True)

    async def on_message_delete(self, message):
        if message.id in self.tracked_messages:
            if self.tracked_messages[message.id] is not None:
                await self.delete_message(self.tracked_messages[message.id])
                self.tracked_messages[message.id] = None

    async def send_message(self, msg, text, response_to=None, parse_content=True, **kwargs):
        text = text.replace(self.token, 'my-token')
        if parse_content:
            text = text.replace('@everyone', '@\u200beveryone')
            text = text.replace('@here', '@\u200bhere')
            text = trim_message(text)

        try:
            message = await msg.channel.send(text, **kwargs)
        except Exception:
            exception = traceback.format_exc()
            exception = '\n'.join(exception.split('\n')[-4:])
            exception = '❗ Message delivery failed\n```\n' + exception + '```'
            message = await msg.channel.send(exception)
        finally:
            if response_to is not None:
                await self.register_response(response_to, message)

            return message

    async def edit_message(self, message, parse_content=True, **fields):
        content = fields.pop('content', '')
        if content:
            content = content.replace(self.token, 'my-token')
            if parse_content:
                content = content.replace('@everyone', '@\u200beveryone')
                content = content.replace('@here', '@\u200bhere')
                content = trim_message(content)

            fields['content'] = content

        try:
            return await message.edit(**fields)
        except discord.errors.NotFound:
            print('edit_message: message not found')
            return
        except Exception:
            exception = traceback.format_exc()
            exception = '\n'.join(exception.split('\n')[-4:])
            exception = '❗ Message edit failed\n```\n' + exception + '```'
            return await message.edit(content=exception)
    
    async def delete_message(self, message):
        try:
            return await message.delete()
        except discord.errors.NotFound:
            print('delete_message: message not found')
            return

    async def track_message(self, message):
        self.tracked_messages[message.id] = None
        self.loop.call_later(300, self.release_tracked_message, message.id)

    def release_tracked_message(self, message_id):
        del self.tracked_messages[message_id]

    async def register_response(self, request, response):
        if request.id in self.tracked_messages:
            self.tracked_messages[request.id] = response
        else:
            print('Request outdated, not registering')


if __name__ == '__main__':
    BotMyBot().run()
