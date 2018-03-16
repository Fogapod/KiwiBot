from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from utils.funcs import find_guild

from discord import Embed, Forbidden, CategoryChannel, VoiceChannel, Colour

import random
from datetime import datetime


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [guild]'
    short_doc = 'Get information about matched guild.'

    name = 'guild'
    aliases = (name, 'server')
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
                    reason=f'requested by {msg.author} ({msg.author.id}) in guild {msg.guild} ({msg.guild.id})',
                    max_age=1800  # 30 minutes
                )
                invite = invite.url
            except Forbidden:
                pass
            
        e = Embed(
            title=guild.name, url=invite,
            description=f'[avatar url]({guild.icon_url_as()})',
            colour=Colour.gold()
        )
        e.set_thumbnail(url=guild.icon_url_as())
        e.add_field(name='owner', value=f'**{guild.owner}** {guild.owner.id}')
        e.add_field(
            name='created', inline=False,
            value=f'`{guild.created_at.replace(microsecond=0)}` ({(datetime.now() - guild.created_at).days} days ago)'
        )

        e.add_field(
            name='members',
            value=f'{guild.member_count} ({sum(1 for m in guild.members if m.bot)} robots)'
        )

        category_channels_num = voice_channels_num = text_channels_num = 0
        for channel in guild.channels:
            if isinstance(channel, CategoryChannel):
                category_channels_num += 1
            elif isinstance(channel, VoiceChannel):
                voice_channels_num += 1
            else:
                text_channels_num += 1

        e.add_field(
            name='channels',
            value=f'{text_channels_num} ({voice_channels_num} voice, {category_channels_num} categories)'
        )

        e.add_field(name='roles', value=len(guild.roles))

        max_emoji = 30
        emoji_num = len(guild.emojis)
        e.add_field(
            name='emojis',
            value=(
                f'**{min(max_emoji, emoji_num)} / {emoji_num}** shown: ' +
                ' '.join(str(e) for e in sorted(random.sample(guild.emojis, min(max_emoji, emoji_num)), key=lambda e: (e.name, e.animated)))
            )
        )

        e.set_footer(text=guild.id)

        await self.send(msg, embed=e)