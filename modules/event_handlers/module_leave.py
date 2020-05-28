from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageGuild

from utils.funcs import find_channel
from utils.formatters import lazy_format

from discord import Forbidden, NotFound, AllowedMentions


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [leave text]'
    short_doc = 'Allows to set message on guild user leave'
    long_doc = (
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
        '\t[--channel|-c] <channel>: use matched channel'
    )

    name = 'leave'
    aliases = (name, )
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
                await member.guild.get_channel(int(channel)).send(
                    leave_message,
                    allowed_mentions=AllowedMentions(
                        everyone=False,
                        roles=False,
                        users=[member.id]
                    )
                )
            except NotFound:
                await self.bot.redis.delete(f'leave_message:{member.guild.id}')
            except Forbidden:
                pass

    async def on_call(self, ctx, args, **flags):
        if len(args) == 1:
            record = await self.bot.redis.get(f'leave_message:{ctx.guild.id}')
            if record:
                channel, _, leave_message = record.partition(':')
                return f'Current leave message: {leave_message}\nChannel: **{channel}**'
            else:
                return await ctx.warn('Leave message not set')

        manage_guild_perm = PermissionManageGuild()
        if not manage_guild_perm.check(ctx.channel, ctx.author):
            raise manage_guild_perm

        if args[1:].lower() in ('delete', 'remove'):
            await self.bot.redis.delete(f'leave_message:{ctx.guild.id}')
            return 'Leave message removed'

        channel_flag = flags.get('channel')
        if channel_flag:
            channel = await find_channel(
                channel_flag, ctx.guild,
                include_voice=False, include_category=False
            )
            if channel is None:
                return await ctx.error('Channel not found')
        else:
            channel = ctx.channel

        text = args[1:]
        if not ctx.channel.permissions_for(ctx.author).mention_everyone:
            text = text.replace('@everyone', '@\u200beveryone')
            text = text.replace('@here', '@\u200bhere')

        await self.bot.redis.set(f'leave_message:{ctx.guild.id}', f'{channel.id}:{text}')
        await self.bot.delete_message(ctx.message)
        await ctx.send(
            f'Set leave message in {channel.mention}', delete_after=7)
