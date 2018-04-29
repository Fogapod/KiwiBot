from objects.logger import Logger

logger = Logger()

from aiohttp import ClientSession

import traceback
import asyncio
import time
import sys

import discord

from objects.modulemanager import ModuleManager
from objects.config import Config
from objects.redisdb import RedisDB

from constants import *

from utils import formatters


class BotMyBot(discord.AutoShardedClient):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # will be used as process exit code after stopping if not None
        self.exit_code = None

        # used to prevent reloading commands in on_ready after reconnect
        self.is_first_on_ready_event = True

        # timestamp of bot launch, filled in first on_ready call
        self.start_time = 0

        self.sess = None

        self.config = Config('config.json', loop=self.loop)
        logger.verbosity = self.config.get('logger_verbosity', logger.VERBOSITY_INFO)
        logger.add_file(self.config.get('logs_file', None))

        logger.debug('Logger ................. connected')

        self.token = self.config.get('token', None)
        self.is_dev = self.config.get('is_dev', False)

        self.mm = ModuleManager(self)
        logger.debug('ModuleManager .......... connected')

        self.redis = RedisDB()
        logger.debug('RedisDB ................ connected')

        self._default_prefix = '+'
        self._mention_prefixes = []
        self.prefixes = []
        self._guild_prefixes = {}

        self._last_messages = {}

    @property
    def uptime(self):
        return time.time() - self.start_time

    async def init_prefixes(self):
        bot_id = self.user.id

        self.prefixes = []
        self._default_prefix = (await self.redis.get('prefix', default='+')).lower()
        self._mention_prefixes = [f'<@{bot_id}>', f'<@!{bot_id}>']
        self.prefixes.extend([self._default_prefix, *self._mention_prefixes])

        self._guild_prefixes = {}
        for key in await self.redis.keys('guild_prefix:*'):
            guild_id = int(key.partition(':')[2])
            self._guild_prefixes[guild_id] = (await self.redis.get(key)).lower()

    def run(self, token=None):
        if token is None:
            token = self.token
        else:
            self.token = token

        if token is None:
            token = input('Token not provided. Please, insert it into config file or paste here for single bot launch: ')

        super().run(token, reconnect=True, fetch_offline_members=True)

    def restart(self):
        self.stop(RESTART_EXIT_CODE)

    def stop(self, exit_code=STOP_EXIT_CODE, force=False):
        if force:
            import sys
            sys.exit(exit_code)
        self.redis.disconnect()
        logger.debug('Stopping event loop and cancelling tasks')
        self.loop.stop()
        tasks = asyncio.gather(*asyncio.Task.all_tasks(), loop=self.loop)
        tasks.cancel()

        self.exit_code = exit_code

    async def on_ready(self):
        if not self.is_first_on_ready_event:
            await self.mm.init_modules()
            logger.info('Bot reconnected')
            return

        self.is_first_on_ready_event = False

        self.sess = ClientSession()

        redis_port = self.config.get('redis_port', None)
        try:
            await self.redis.connect(port=redis_port)
        except ConnectionRefusedError:
            logger.info('Failed to connect to redis! Stopping bot')
            logger.info(traceback.format_exc())
            self.stop(ERROR_EXIT_CODE, force=True)
        logger.info('Connected to redis db with %s keys' % await self.redis.get_db_size())

        await self.mm.load_modules(strict_mode=False)
        logger.info('Loaded modules: [%s]' % ' '.join(self.mm.modules.keys()))

        await self.init_prefixes()

        self.start_time = time.time()
        logger.info(ASCII_ART)
        logger.info(f'Logged in as {self.user} with {len(self.guilds)} guilds')
        logger.info('Bot ready, good luck!')

        if self.is_dev:
            logger.info('Is a dev instance')

        logger.info('Default prefix: ' + self._default_prefix)

    async def close(self):
        await super().close()
        logger.info('Connection closed')

    async def on_message(self, msg, from_edit=False):
        self.register_last_user_message(msg)

        if msg.author.bot:
            return

        if not from_edit:
            await self.track_message(msg)

        lower_content = msg.content.lower()
        clean_content = None

        prefixes = self.prefixes

        if msg.guild is not None:
            guild_prefixes = self._guild_prefixes.get(msg.guild.id, None)

            if guild_prefixes:
                prefixes = [guild_prefixes] + self._mention_prefixes
        else:
            prefixes = prefixes + ['']

        for p in prefixes:
            if lower_content.startswith(p):
                clean_content = msg.content[len(p):].lstrip()
                break

        if clean_content is None:
            return

        module_response = await self.mm.check_modules(msg, clean_content)

        if module_response:
            if isinstance(module_response, discord.Message):
                return

            module_response = await formatters.format_response(
                module_response, msg, self)

        if module_response:
            await self.send_message(
                msg.channel, content=module_response, response_to=msg)

    def register_last_user_message(self, msg):
        if msg.channel.id not in self._last_messages:
            self._last_messages[msg.channel.id] = {msg.author.id: msg}
        else:
            self._last_messages[msg.channel.id][msg.author.id] = msg

    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        if before.content == after.content:
            return

        if await self.redis.exists(f'tracked_message:{before.id}'):
            await self.clear_responses_to_message(before)
            ttl = await self.redis.ttl(f'tracked_message:{before.id}')
            await self.redis.expire(f'tracked_message:{before.id}', ttl + 60)

            await self.on_message(after, from_edit=True)

    async def on_message_delete(self, msg):
        if await self.redis.exists(f'tracked_message:{msg.id}'):
            await self.clear_responses_to_message(msg)
        await self.redis.delete(f'tracked_message:{msg.id}')

    async def clear_responses_to_message(self, msg):
        for mid in (await self.redis.smembers(f'tracked_message:{msg.id}'))[1:]:
            try:
                await self.http.delete_message(msg.channel.id, int(mid))
            except Exception:
                pass

    async def send_message(self, channel, response_to=None, replace_mass_mentions=True, replace_mentions=True, **fields):
        content = fields.pop('content', '')
        content = content.replace(self.token, 'TOKEN_LEAKED')

        if replace_mentions:
            content = await formatters.replace_mentions(content, channel, self)
        if replace_mass_mentions:
            content = formatters.replace_mass_mentions(content)

        content = formatters.trim_text(content)
        fields['content'] = content

        message = None
        # dm_message = None

        try:
            message = await channel.send(**fields)
        except discord.Forbidden:
            # try:
            #     dm_message = await msg.author.send(
            #         f'I was not able to send this message to channel '
            #         f'{msg.channel.mention} in guild **{msg.guild}**, result is below'
            #     )
            #     message = await msg.author.send(**fields)
            # except Exception:
            #     pass
            pass
        except Exception:
            exception = traceback.format_exc()
            exception = '\n'.join(exception.split('\n')[-4:])
            exception = f'❗ Message delivery failed\n```\n{exception}```'
            message = await channel.send(exception)
        finally:
            if response_to is not None:
                if message is not None:
                    await self.register_response(response_to, message)
                # if dm_message is not None:
                #     await self.register_response(response_to, dm_message)

            return message

    async def edit_message(self, msg, replace_mass_mentions=True, replace_mentions=True, **fields):
        content = fields.pop('content', '')
        content = content.replace(self.token, 'TOKEN_LEAKED')

        if replace_mentions:
            content = await formatters.replace_mentions(content, msg.channel, self)
        if replace_mass_mentions:
            content = formatters.replace_mass_mentions(content)

        content = formatters.trim_text(content)
        fields['content'] = content

        try:
            return await msg.edit(**fields)
        except discord.errors.NotFound:
            logger.debug('edit_message: message not found')
            return None
        except Exception:
            exception = traceback.format_exc()
            exception = '\n'.join(exception.split('\n')[-4:])
            exception = f'❗ Message edit failed\n```\n{exception}```'
            return await msg.edit(content=exception)
    
    async def delete_message(self, message, raise_on_errors=False):
        try:
            return await message.delete()
        except discord.errors.NotFound:
            logger.debug('delete_message: message not found')
            return
        except Exception:
            if raise_on_errors:
                raise

    async def track_message(self, message):
        if await self.redis.exists(f'tracked_message:{message.id}'):
            return

        await self.redis.sadd(f'tracked_message:{message.id}', '0')
        await self.redis.expire(f'tracked_message:{message.id}', 300)

    async def register_response(self, request, response):
        if await self.redis.exists(f'tracked_message:{request.id}'):
            await self.redis.sadd(f'tracked_message:{request.id}', response.id)
        else:
            logger.debug('Request outdated, not registering')

    def dispatch(self, event, *args, **kwargs):
        super().dispatch(event, *args, **kwargs)

        for module in self.mm.modules.values():
            handler = module.events.get(event)
            if handler:
                coro = self._run_event(handler, event, *args, **kwargs)
                discord.compat.create_task(coro, loop=self.loop)