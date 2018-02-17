import traceback
import asyncio
import time
import sys

import discord

from modulemanager import ModuleManager

from utils.constants import DEFAULT_PREFIXES, STOP_EXIT_CODE
from utils.formatters import format_response, trim_message
from utils.config import Config
from utils.logger import Logger


EXIT_CODE = None


class BotMyBot(discord.Client):

    def __init__(self, *args, **kwargs):
        super(BotMyBot, self).__init__(*args, **kwargs)
        # used to prevent reloading commands in on_ready after reconnect
        self.is_first_on_ready_event = True

        self.start_time = 0

        self.config = Config('config.json', loop=self.loop)
        self.token = self.config.get('token', None)

        self.logger = Logger(file=self.config.get('logs_file', None))
        self.logger.verbosity = self.config.get('logger_verbosity', self.logger.VERBOSITY_INFO)
        self.logger.debug('Logger connected')

        self.tracked_messages = {}
        self.mm = ModuleManager(self)
        self.logger.debug('ModuleManager connected')

        self.prefixes = DEFAULT_PREFIXES

    def run(self, token=None):
        if token is None:
            token = self.token
        else:
            self.token = token

        if token is None:
            self.loop.run_until_complete(self.close())
            self.stop(1)
            raise discord.LoginFailure('No token provided')

        super(BotMyBot, self).run(token, reconnect=True)

    def restart(self):
        self.stop(0)

    def stop(self, exit_code=STOP_EXIT_CODE):
        self.logger.debug('Stopping event loop and cancelling tasks')
        self.loop.stop()
        tasks = asyncio.gather(*asyncio.Task.all_tasks(), loop=self.loop)
        tasks.cancel()

        self.logger.debug('Preparing to exit with code ' + str(exit_code))
        global EXIT_CODE
        EXIT_CODE = exit_code

    async def on_ready(self):
        if not self.is_first_on_ready_event:
            await self.mm.init_modules()
            self.logger.info('Bot reconnected')
            return

        self.is_first_on_ready_event = False

        await self.mm.load_modules()
        self.logger.info('Loaded modules: [%s]' % ' '.join(self.mm.modules.keys()))
        self.start_time = time.time()
        self.logger.info('Bot ready')
        self.logger.info('Default prefix: ' + self.prefixes[0])

    async def close(self):
        await super(BotMyBot, self).close()
        self.logger.info('Connection closed')

    async def on_message(self, message, from_edit=False):
        if message.author.bot:
            return

        if message.guild is None:
            await self.send_message(
                message, 'Direct messages are not supported yet')
            return

        if not from_edit:
            await self.track_message(message)

        lower_content = message.content.lower()

        if not lower_content.startswith(self.prefixes):
            return

        message.content = message.content[
            len(next(p for p in self.prefixes if lower_content.startswith(p))):].strip()

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
            self.logger.debug('edit_message: message not found')
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
            self.logger.debug('delete_message: message not found')
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
            self.logger.debug('Request outdated, not registering')


if __name__ == '__main__':
    BotMyBot().run()
    if EXIT_CODE is not None:
        sys.exit(EXIT_CODE)