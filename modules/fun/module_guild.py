from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from utils.funcs import find_guild

from discord import Embed, Forbidden, VoiceChannel, TextChannel, Colour

import random
from datetime import datetime


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [guild]'
    short_doc = 'Get information about matched guild.'

    name = 'guild'
    aliases = (name, 'guildinfo', 'server', 'serverinfo')
    required_perms = (PermissionEmbedLinks, )

    async def on_call(self, msg, *args, **flags):
        if len(args) == 1:
            guild = msg.guild
        else:
            guild = await find_guild(
                msg.content.partition(args[0])[2].lstrip(),
                self.bot
            )

        if guild is None:
            return '{warning} Guild not found'

        invite = ''
        if guild != msg.guild:
            try:
                invite = await guild.channels[0].create_invite(
                    reason=f'requested by {msg.author} ({msg.author.id})' + (f' in guild {msg.guild} {msg.guild.id})' if msg.guild else ''),
                    max_age=1800  # 30 minutes
                )
                invite = invite.url
            except Forbidden:
                pass
            
        e = Embed(
            title=guild.name, url=invite,
            colour=Colour.gold()
        )
        if guild.icon_url:
            e.description = f'[avatar url]({guild.icon_url})'
            e.set_thumbnail(url=guild.icon_url)
        else:
            # TODO: custom thumbnail for this case
            pass

        e.add_field(name='owner', value=f'**{guild.owner}** {guild.owner.id}')
        e.add_field(
            name='created', inline=False,
            value=f'`{guild.created_at.replace(microsecond=0)}` ({(datetime.now() - guild.created_at).days} days ago)'
        )

        bot_count = sum(1 for m in guild.members if m.bot)

        e.add_field(
            name='members',
            value=f'{guild.member_count - bot_count} + {bot_count} robots'
        )

        voice_channels_num = text_channels_num = 0
        for channel in guild.channels:
            if isinstance(channel, VoiceChannel):
                voice_channels_num += 1
            elif isinstance(channel, TextChannel):
                text_channels_num += 1

        e.add_field(
            name='channels',
            value=f'{text_channels_num} text, {voice_channels_num} voice'
        )

        e.add_field(name='roles', value=len(guild.roles))

        max_emoji = 30
        emoji_num = len(guild.emojis)
        e.add_field(
            name='emojis',
            value=(
                f'**{min(max_emoji, emoji_num)} / {emoji_num}** shown: ' +
                ' '.join(str(e) for e in sorted(random.sample(guild.emojis, min(max_emoji, emoji_num)), key=lambda e: (e.animated, e.name)))
            ) if guild.emojis else 'Guild does not have them :/',
            inline=False
        )

        e.set_footer(text=guild.id)

        await self.send(msg, embed=e)