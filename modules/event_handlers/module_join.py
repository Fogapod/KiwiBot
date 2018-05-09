from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageGuild

from utils.funcs import find_channel
from utils.formatters import lazy_format

from discord import Forbidden, NotFound


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [welcome text]'
    short_doc = 'Allows to set message on guild user join'
    long_doc = (
        'See current join message:\n'
        '\t{prefix}{aliases}\n\n'
        'Remove welcome message:\n'
        '\t{prefix}{aliases} delete" or {prefix}{aliases} remove\n\n'
        'Welcome message support several keys.\n'
        'Keys are replaced to match user.\n'
        'Currently available keys:\n'
        '\t{mention} - @mentions user\n'
        '\t{name} - user name\n'
        '\t{discrim} - user discriminator\n'
        '\t{guild} - guild name\n'
        '\t{id} - user id\n\n'
        'Command flags:\n'
        '\t--channel or -c <channel> - use matched channel'
    )

    name = 'join'
    aliases = (name, 'welcome')
    category = 'Moderation'
    flags = {
        'channel': {
            'alias': 'c',
            'bool': False
        }
    }
    guild_only = True

    async def on_load(self, from_reload):
        self.events = {
            'member_join': self.on_member_join
        }

    async def on_member_join(self, member):
        record = await self.bot.redis.get(f'join_message:{member.guild.id}')
        if record:
            channel, _, join_message = record.partition(':')
            join_message = lazy_format(
                join_message,
                mention=member.mention,
                name=member.name,
                discrim=member.discriminator,
                guild=member.guild.name,
                id=member.id
            )
            try:
                await member.guild.get_channel(int(channel)).send(join_message)
            except NotFound:
                await self.bot.redis.delete(f'join_message:{member.guild.id}')
            except Forbidden:
                pass

    async def on_call(self, msg, args, **flags):
        if len(args) == 1:
            record = await self.bot.redis.get(f'join_message:{msg.guild.id}')
            if record:
                channel, _, join_message = record.partition(':')
                return f'Current join message: {join_message}\nChannel: **{channel}**'
            else:
                 return '{warning} Welcome message not set'

        manage_guild_perm = PermissionManageGuild()
        if not manage_guild_perm.check(msg.channel, msg.author):
            raise manage_guild_perm

        if args[1:].lower() in ('delete', 'remove'):
            await self.bot.redis.delete(f'join_message:{msg.guild.id}')
            return 'Welcome message removed'

        channel_flag = flags.get('channel')
        if channel_flag:
            channel = await find_channel(
                channel_flag, msg.guild, self.bot,
                include_voice=False, include_category=False
            )
            if channel is None:
                return '{error} Channel not found'
        else:
            channel = msg.channel

        text = args[1:]
        if not msg.channel.permissions_for(msg.author).mention_everyone:
            text = text.replace('@everyone', '@\u200beveryone')
            text = text.replace('@here', '@\u200bhere')

        await self.bot.redis.set(f'join_message:{msg.guild.id}', f'{msg.channel.id}:{text}')
        await self.bot.delete_message(msg)
        await self.send(
            msg, delete_after=7,
            content=f'Set welcome message in {channel.mention}'
        )