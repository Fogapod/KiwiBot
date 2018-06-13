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
from objects.context import Context

from constants import *

from utils import formatters


class KiwiBot(discord.AutoShardedClient):

    _bot = None

    def __init__(self, **kwargs):
        KiwiBot._bot = self

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
        self._leave_voice_channel_tasks = {}

    @staticmethod
    def get_bot():
        return KiwiBot._bot

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
            token = self.config.get('token', None)

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
        self.register_last_user_message_timestamp(msg)

        if msg.author.bot:
            return

        if not from_edit:
            await self.track_message(msg)

        lower_content = msg.content.lower()

        prefixes = self.prefixes

        if msg.guild is not None:
            guild_prefixes = self._guild_prefixes.get(msg.guild.id, None)

            if guild_prefixes:
                prefixes = [guild_prefixes] + self._mention_prefixes
        else:
            prefixes = prefixes + ['']

        prefix = None
        for p in prefixes:
            if lower_content.startswith(p):
                prefix = p
                break

        if prefix is None:
            return

        await self.process_command(
            Context(self, msg, prefix), msg.content[len(p):].lstrip())

    async def process_command(self, ctx, clean_content):
        module_response = await self.mm.check_modules(ctx, clean_content)

        if module_response:
            if not isinstance(module_response, str):
                return

            module_response = await formatters.format_response(
                module_response, ctx.message, self)

        if module_response:
            await ctx.send(module_response)

    def register_last_user_message_timestamp(self, msg):
        # await self.redis.set(
        #     f'last_message_timestamp:{msg.channel.id}:{msg.author.id}',
        #     msg.created_at.timestamp(), 'EX', 86400
        # )

        if msg.channel.id not in self._last_messages:
            self._last_messages[msg.channel.id] = { msg.author.id: msg.edited_at or msg.created_at}
        else:
            self._last_messages[msg.channel.id][msg.author.id] = msg.edited_at or msg.created_at

    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        if before.content == after.content:
            return

        if await self.redis.exists(f'tracked_message:{before.id}'):
            await self.clear_responses_to_message(before.id)
            ttl = await self.redis.ttl(f'tracked_message:{before.id}')
            await self.redis.expire(f'tracked_message:{before.id}', ttl + 60)

            await self.on_message(after, from_edit=True)

    async def on_raw_message_delete(self, event):
        if await self.redis.exists(f'tracked_message:{event.message_id}'):
            await self.clear_responses_to_message(event.message_id)
        await self.redis.delete(f'tracked_message:{event.message_id}')

    async def clear_responses_to_message(self, msg_id):
        for value in await self.redis.lrange(f'tracked_message:{msg_id}', 1, -1):
            response_type, _, rest = value.partition(':')

            if response_type == 'message':
                channel_id, message_id = rest.split(':')
                try:
                    await self.http.delete_message(int(channel_id), int(message_id))
                except Exception:
                    pass
            elif response_type == 'reaction':
                channel_id, message_id, reaction = rest.split(':', 2)
                if reaction.isdigit():
                    e = self.get_emoji(int(reaction))
                    emoji = f'{"a:" if e.animated else ""}{e.name}:{e.id}'
                    if emoji is None:
                        return
                else:
                    emoji = reaction
                try:
                    await self.http.remove_own_reaction(
                        int(message_id), int(channel_id), emoji)
                except Exception as e:
                    pass

        await self.redis.execute('LTRIM', f'tracked_message:{msg_id}', 0, 0)

    async def on_voice_state_update(self, member, before, after):
        if not member.guild.me.voice:  # voice connection doesn't exist
            return

        if before.channel and after.channel != before.channel:  # user left or moved
            if not member.bot or member == self.user:  # action by user or bot was moved
                if sum(1 for m in before.channel.members if not m.bot) == 0:  # no users in channel left
                    self._leave_voice_channel_tasks[before.channel.id] = self.loop.create_task(
                        self._voice_disconnect_task(before.channel, member.guild.voice_client))

        elif after.channel and not before.channel:  # user joined
            if member.guild.me.voice.channel == after.channel and not member.bot:  # same channel and not bot
                if after.channel.id in self._leave_voice_channel_tasks:
                    self._leave_voice_channel_tasks[after.channel.id].cancel()
                    del self._leave_voice_channel_tasks[after.channel.id]

    async def _voice_disconnect_task(self, channel, vc):
        await asyncio.sleep(60)
        if sum(1 for m in channel.members if not m.bot) > 0:  # there are users in channel
            return

        del self._leave_voice_channel_tasks[channel.id]

        if vc.is_connected():
            await vc.disconnect()

    async def send_message(self, target, content=None, *, response_to=None, replace_mass_mentions=True, replace_mentions=True, **fields):
        if isinstance(target, discord.Member) or isinstance(target, discord.User):
            if target.dm_channel is None:
                channel = await target.create_dm()
            else:
                channel = target.dm_channel
        elif isinstance(target, (discord.Message, Context)):
            channel = target.channel
        elif isinstance(target, (discord.DMChannel, discord.TextChannel, discord.Webhook)):
            channel = target
        else:
            raise ValueError('Unknown target passed to send message')

        content = str(content) if content is not None else ''
        content = content.replace(self.http.token, 'TOKEN_LEAKED')

        if replace_mentions:
            content = await formatters.replace_mentions(content, channel, self)
        if replace_mass_mentions:
            content = formatters.replace_mass_mentions(content)

        fields['content'] = formatters.trim_text(content)

        message = None
        dm_message = None

        try:
            message = await channel.send(**fields)
        except discord.Forbidden:
            if response_to is not None:
                try:
                    error_dm_message = await response_to.author.send(
                        f'I was not able to send this message to channel '
                        f'{channel.mention} in guild **{response_to.guild}**, result is below'
                    )
                    await self.register_response(response_to, error_dm_message)
                    dm_message = await response_to.author.send(**fields)
                    await self.register_response(response_to, dm_message)
                except Exception:
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

        return message or dm_message

    async def edit_message(self, msg, content=None, *, replace_mass_mentions=True, replace_mentions=True, **fields):
        content = str(content) if content is not None else ''
        content = content.replace(self.http.token, 'TOKEN_LEAKED')

        if replace_mentions:
            content = await formatters.replace_mentions(content, msg.channel, self)
        if replace_mass_mentions:
            content = formatters.replace_mass_mentions(content)

        fields['content'] = formatters.trim_text(content)

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
        if message is None:
            return

        try:
            return await message.delete()
        except Exception:
            if raise_on_errors:
                raise

    async def add_reaction(self, target, reaction, response_to=None, raise_on_errors=False):
        if isinstance(target, Context):
            message = target.message
        elif isinstance(target, discord.Message):
            message = target
        else:
            raise ValueError(f'Unknown target type is passed: {type(target)}. Expected {Context} or {discord.Message}')

        reaction_type = type(reaction)
        if reaction_type is str:  # unicode
            emoji = reaction
        elif reaction_type is int:  # id
            emoji = self.get_emoji(reaction)
            if emoji is None:
                if raise_on_errors:
                    raise ValueError(f'Emoji with if {emoji} not found in cache')
                else:
                    return
        elif reaction_type is discord.Emoji:
            emoji = reaction
        else:
            raise ValueError(f'Unknown emoji type is passed: {type(reaction)}. Expected one of {discord.Emoji}, {str}, {int}')

        try:
            await message.add_reaction(emoji)
        except Exception as e:
            if raise_on_errors:
                raise e
        else:
            if response_to is not None:
                await self.register_reaction_response(
                    response_to, message, emoji)

    async def track_message(self, message):
        if await self.redis.exists(f'tracked_message:{message.id}'):
            return

        await self.redis.rpush(f'tracked_message:{message.id}', 0)  # insert 0 to prevent key from deleting
        await self.redis.expire(f'tracked_message:{message.id}', 86400)  # 24 hours

    async def register_response(self, request, response):
        if await self.redis.exists(f'tracked_message:{request.id}'):
            await self.redis.rpush(
                f'tracked_message:{request.id}',
                f'message:{response.channel.id}:{response.id}'
            )

    async def register_reaction_response(self, request, message, emoji):
        if isinstance(emoji, discord.Emoji):
            emoji = emoji.id

        if await self.redis.exists(f'tracked_message:{request.id}'):
            await self.redis.rpush(
                f'tracked_message:{request.id}',
                f'reaction:{message.channel.id}:{message.id}:{emoji}'
            )

    def dispatch(self, event, *args, **kwargs):
        super().dispatch(event, *args, **kwargs)

        for module in self.mm.modules.values():
            handler = module.events.get(event)
            if handler:
                coro = self._run_event(handler, event, *args, **kwargs)
                asyncio.ensure_future(coro, loop=self.loop)