import traceback
import asyncio
import time
import sys

import discord

from utils.logger import Logger

logger = Logger()

from modulemanager import ModuleManager

from utils.constants import STOP_EXIT_CODE
from utils.formatters import format_response, trim_message
from utils.config import Config
from redisdb import RedisDB


EXIT_CODE = None

class BotMyBot(discord.Client):

    def __init__(self, *args, **kwargs):
        super(BotMyBot, self).__init__(*args, **kwargs)
        # used to prevent reloading commands in on_ready after reconnect
        self.is_first_on_ready_event = True

        self.start_time = 0
        self.tracked_messages = {}

        self.config = Config('config.json', loop=self.loop)
        logger.verbosity = self.config.get('logger_verbosity', logger.VERBOSITY_INFO)
        logger.add_file(self.config.get('logs_file', None))

        logger.debug('Logger ................. connected')

        self.token = self.config.get('token', None)

        self.mm = ModuleManager(self)
        logger.debug('ModuleManager .......... connected')

        self.redis = RedisDB()
        logger.debug('RedisDB ................ connected')

        self.prefixes = []

    async def init_prefixes(self):
        bot_id = self.user.id

        self.prefixes = []
        self._default_prefix = await self.redis.get('prefix', default='+')
        self._mention_prefixes = [f'<@{bot_id}>', f'<!@{bot_id}>']
        self.prefixes.extend([self._default_prefix, *self._mention_prefixes])

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
        self.redis.disconnect()
        logger.debug('Stopping event loop and cancelling tasks')
        self.loop.stop()
        tasks = asyncio.gather(*asyncio.Task.all_tasks(), loop=self.loop)
        tasks.cancel()

        global EXIT_CODE
        EXIT_CODE = exit_code

    async def on_ready(self):
        if not self.is_first_on_ready_event:
            await self.mm.init_modules()
            logger.info('Bot reconnected')
            return

        self.is_first_on_ready_event = False

        await self.redis.connect()
        logger.info('Connected to redis db with %s keys' % await self.redis.get_db_size())

        await self.mm.load_modules()
        logger.info('Loaded modules: [%s]' % ' '.join(self.mm.modules.keys()))

        await self.init_prefixes()

        self.start_time = time.time()
        logger.info('Bot ready')
        logger.info('Default prefix: ' + self._default_prefix)

    async def close(self):
        await super(BotMyBot, self).close()
        logger.info('Connection closed')

    async def on_message(self, msg, from_edit=False):
        if msg.author.bot:
            return

        prefix_override = False

        if msg.guild is None:
            await self.send_message(
                msg, 'Direct messages are not supported yet')
            return
        else:
            prefix_override = await self.redis.get(f'guild_prefix:{msg.guild.id}')

        if not from_edit:
            await self.track_message(msg)

        lower_content = msg.content.lower()
        clean_content = None

        for p in self.prefixes if prefix_override is None else [prefix_override] + self.prefixes[1:]:
            if lower_content.startswith(p):
                clean_content = msg.content[len(p):].lstrip()
                break

        if clean_content is None:
            return

        module_response = await self.mm.check_modules(msg, clean_content)

        if module_response:
            module_response = await format_response(
                module_response, msg, self)

        if module_response:
            await self.send_message(
                msg, module_response, response_to=msg)

    async def on_message_edit(self, before, after):
        if before.content == after.content:
            return

        if before.id in self.tracked_messages:
            await self.clear_responses_to_message(before.id)
            await self.on_message(after, from_edit=True)

    async def on_message_delete(self, message):
        if message.id in self.tracked_messages:
            await self.clear_responses_to_message(message.id)

    async def clear_responses_to_message(self, message_id):
        if len(self.tracked_messages[message_id]) > 0:
            for message in self.tracked_messages[message_id]:
                await self.delete_message(message)
            self.tracked_messages[message_id] = []

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
            exception = f'❗ Message delivery failed\n```\n{exception}```'
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
            logger.debug('edit_message: message not found')
            return
        except Exception:
            exception = traceback.format_exc()
            exception = '\n'.join(exception.split('\n')[-4:])
            exception = f'❗ Message edit failed\n```\n{exception}```'
            return await message.edit(content=exception)
    
    async def delete_message(self, message):
        try:
            return await message.delete()
        except discord.errors.NotFound:
            logger.debug('delete_message: message not found')
            return

    async def track_message(self, message):
        if message.id in self.tracked_messages:
            return

        self.tracked_messages[message.id] = []
        self.loop.call_later(300, self.release_tracked_message, message.id)

    def release_tracked_message(self, message_id):
        del self.tracked_messages[message_id]

    async def register_response(self, request, response):
        if request.id in self.tracked_messages:
            self.tracked_messages[request.id].append(response)
        else:
            logger.debug('Request outdated, not registering')


if __name__ == '__main__':
    BotMyBot().run()
    if EXIT_CODE is not None:
        logger.debug(f'Exiting with code {EXIT_CODE}')
        sys.exit(EXIT_CODE)