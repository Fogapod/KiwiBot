from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageGuild

from utils.funcs import find_channel
from utils.formatters import lazy_format

from discord import Forbidden, NotFound, AllowedMentions


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
        '\t[--channel|-c] <channel>: use matched channel'
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
                await member.guild.get_channel(int(channel)).send(
                    join_message,
                    allowed_mentions=AllowedMentions(
                        everyone=False,
                        roles=False,
                        users=[member]
                    )
                )
            except NotFound:
                await self.bot.redis.delete(f'join_message:{member.guild.id}')
            except Forbidden:
                pass

    async def on_call(self, ctx, args, **flags):
        if len(args) == 1:
            record = await self.bot.redis.get(f'join_message:{ctx.guild.id}')
            if record:
                channel, _, join_message = record.partition(':')
                return f'Current join message: {join_message}\nChannel: **{channel}**'
            else:
                 return await ctx.warn('Welcome message not set')

        manage_guild_perm = PermissionManageGuild()
        if not manage_guild_perm.check(ctx.channel, ctx.author):
            raise manage_guild_perm

        if args[1:].lower() in ('delete', 'remove'):
            await self.bot.redis.delete(f'join_message:{ctx.guild.id}')
            return 'Welcome message removed'

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

        await self.bot.redis.set(f'join_message:{ctx.guild.id}', f'{channel.id}:{text}')
        await self.bot.delete_message(ctx.message)
        await ctx.send(
            f'Set welcome message in {channel.mention}', delete_after=7)
