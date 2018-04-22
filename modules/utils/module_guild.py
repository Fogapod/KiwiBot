from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks, PermissionExternalEmojis

from utils.funcs import find_guild

from discord import Embed, Forbidden, VoiceChannel, TextChannel, Colour

import random
from datetime import datetime


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [guild]'
    short_doc = 'Get information about matched guild.'

    name = 'guild'
    aliases = (name, 'guildinfo', 'server', 'serverinfo')
    required_perms = (PermissionEmbedLinks(), )

    async def on_call(self, msg, args, **flags):
        if len(args) == 1:
            guild = msg.guild
        else:
            guild = await find_guild(args[1:], self.bot)

        if guild is None:
            return '{warning} Guild not found'

        invite = ''

        if guild == msg.guild:
            top_role = guild.role_hierarchy[0].mention
        else:
            try:
                invite = await guild.channels[0].create_invite(
                    reason=f'requested by {msg.author} ({msg.author.id})' + (f' in guild {msg.guild} {msg.guild.id})' if msg.guild else ''),
                    max_age=3600 * 12  # 12 hours
                )
            except Forbidden:
                pass
            else:
                invite = invite.url

            top_role = f'@{guild.role_hierarchy[0]}'

        bot_count = sum(1 for m in guild.members if m.bot)

        voice_channels_num = text_channels_num = 0
        for channel in guild.channels:
            if isinstance(channel, VoiceChannel):
                voice_channels_num += 1
            elif isinstance(channel, TextChannel):
                text_channels_num += 1

        max_emoji = 30

        static_emojis = []
        animated_emojis = []
        for em in guild.emojis or []:
            (static_emojis, animated_emojis)[em.animated].append(em)

        e = Embed(
            title=guild.name, url=invite,
            colour=Colour.gold()
        )
        if guild.icon_url:
            e.set_thumbnail(url=guild.icon_url)
        else:
            # TODO: custom thumbnail for this case
            pass

        e.add_field(
            name='created', inline=False,
            value=f'`{guild.created_at.replace(microsecond=0)}` ({(datetime.now() - guild.created_at).days} days ago)'
        )
        e.add_field(name='owner', value=guild.owner.mention)
        e.add_field(name='region', value=guild.region)
        e.add_field(
            name='members',
            value=f'{guild.member_count - bot_count} + {bot_count} robots'
        )
        e.add_field(
            name='channels',
            value=f'{text_channels_num} text, {voice_channels_num} voice'
        )
        e.add_field(name='total roles', value=len(guild.roles))
        e.add_field(name='top role', value=top_role)
        if guild.icon_url:
            formats = ['png', 'webp', 'jpg']
            e.add_field(
                name='avatar',
                value=' | '.join(f'[{f}]({guild.icon_url_as(format=f)})' for f in formats)
            )
        if guild == msg.guild or PermissionExternalEmojis().check(msg.channel, self.bot.user):
            e.add_field(
                name='static emotes', inline=False,
                value=(
                    f'**{min(max_emoji, len(static_emojis))} / {len(static_emojis)}** shown: ' +
                    ' '.join(
                        str(e) for e in sorted(
                            random.sample(static_emojis, min(max_emoji, len(static_emojis))),
                            key=lambda e: e.name))
                ) if static_emojis else 'Guild does not have them :/'
            )
            e.add_field(
                name='animated emotes', inline=False,
                value=(
                    f'**{min(max_emoji, len(animated_emojis))} / {len(animated_emojis)}** shown: ' +
                    ' '.join(
                        str(e) for e in sorted(
                            random.sample(animated_emojis, min(max_emoji, len(animated_emojis))),
                            key=lambda e: e.name
                        )
                    )
                ) if animated_emojis else 'Guild does not have them :/'
            )
        else:
            e.add_field(
                name='emojis', value='I have no permission to show external emojis', inline=False)
        e.set_footer(text=guild.id)

        await self.send(msg, embed=e)