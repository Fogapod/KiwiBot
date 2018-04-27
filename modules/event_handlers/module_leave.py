from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageGuild

from utils.funcs import find_channel
from utils.formatters import lazy_format

from discord import Forbidden, NotFound


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [leave text]'
    short_doc = 'Allows to set message on guild user leave.'
    additional_doc = (
        'See current leave message:\n'
        '\t{prefix}{aliases}\n\n'
        'Remove leave message:\n'
        '\t{prefix}{aliases} delete" or {prefix}{aliases} remove\n\n'
        'Leave message support several keys.\n'
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

    name = 'leave'
    aliases = (name, )
    call_flags = {
        'channel': {
            'alias': 'c',
            'bool': False
        }
    }
    guild_only = True

    async def on_load(self, from_reload):
        self.events = {
            'member_remove': self.on_member_leave
        }

    async def on_member_leave(self, member):
        record = await self.bot.redis.get(f'leave_message:{member.guild.id}')
        if record:
            channel, _, leave_message = record.partition(':')
            leave_message = lazy_format(
                leave_message,
                mention=member.mention,
                name=member.name,
                discrim=member.discriminator,
                guild=member.guild.name,
                id=member.id
            )
            try:
                await member.guild.get_channel(int(channel)).send(leave_message)
            except NotFound:
                await self.bot.redis.delete(f'leave_message:{member.guild.id}')
            except Forbidden:
                pass

    async def on_call(self, msg, args, **flags):
        if len(args) == 1:
            record = await self.bot.redis.get(f'leave_message:{msg.guild.id}')
            if record:
                channel, _, leave_message = record.partition(':')
                return f'Current leave message: {leave_message}\nChannel: **{channel}**'
            else:
                return '{warning} Leave message not set'

        manage_guild_perm = PermissionManageGuild()
        if not manage_guild_perm.check(msg.channel, msg.author):
            raise manage_guild_perm

        if args[1:].lower() in ('delete', 'remove'):
            await self.bot.redis.delete(f'leave_message:{msg.guild.id}')
            return 'Leave message removed'

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

        await self.bot.redis.set(f'leave_message:{msg.guild.id}', f'{channel.id}:{text}')
        await self.bot.delete_message(msg)
        await self.send(
            msg, delete_after=7,
            content=f'Set leave message in {channel.mention}'
        )