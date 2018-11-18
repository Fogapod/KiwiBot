from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks, PermissionExternalEmojis

from utils.funcs import find_guild

from discord import Embed, VoiceChannel, TextChannel, Colour

import random
from datetime import datetime


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [guild]'
    short_doc = 'Shows matched guild info'

    name = 'guild'
    aliases = (name, 'guildinfo', 'server', 'serverinfo')
    category = 'Discord'
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **flags):
        if len(args) == 1:
            guild = ctx.guild
        else:
            guild = await find_guild(args[1:])

        if guild is None:
            return await ctx.warn('Guild not found')

        if guild == ctx.guild:
            top_role = guild.roles[-1].mention
        else:
            top_role = f'@{guild.roles[-1]}'

        bot_count = sum(1 for m in guild.members if m.bot)

        voice_channels_num, text_channels_num = 0, 0
        for channel in guild.channels:
            if isinstance(channel, VoiceChannel):
                voice_channels_num += 1
            elif isinstance(channel, TextChannel):
                text_channels_num += 1

        max_emoji = 25

        static_emojis = []
        animated_emojis = []
        for em in guild.emojis or []:
            (static_emojis, animated_emojis)[em.animated].append(em)

        e = Embed(title=guild.name, colour=Colour.gold())

        if guild.icon_url:
            e.set_thumbnail(url=guild.icon_url)
        else:
            # TODO: custom thumbnail for this case
            pass

        e.add_field(
            name='Created at', inline=False,
            value=f'`{guild.created_at.replace(microsecond=0)}` ({(datetime.now() - guild.created_at).days} days ago)'
        )
        e.add_field(name='Owner', value=guild.owner.mention)
        e.add_field(name='Region', value=guild.region)
        e.add_field(
            name='Members',
            value=f'{guild.member_count - bot_count} + {bot_count} robots'
        )
        e.add_field(
            name='Channels',
            value=f'{text_channels_num} text, {voice_channels_num} voice'
        )
        e.add_field(name='Total roles', value=len(guild.roles) - 1)
        e.add_field(name='Top role', value=top_role)
        if guild.icon_url:
            formats = ['png', 'webp', 'jpg']
            e.add_field(
                name='Icon',
                value=' | '.join(f'[{f}]({guild.icon_url_as(format=f)})' for f in formats)
            )
        if guild == ctx.guild or PermissionExternalEmojis().check(ctx.channel, self.bot.user):
            e.add_field(
                name=f'Static emotes ({min(max_emoji, len(static_emojis))} / {len(static_emojis)}) shown',
                inline=False, value=' '.join(
                    str(e) for e in sorted(
                        random.sample(static_emojis, min(max_emoji, len(static_emojis))),
                        key=lambda e: e.name)
                    ) if static_emojis else 'Guild does not have any'
            )
            e.add_field(
                name=f'Animated emotes ({min(max_emoji, len(animated_emojis))} / {len(animated_emojis)}) shown',
                inline=False, value=' '.join(
                    str(e) for e in sorted(
                        random.sample(animated_emojis, min(max_emoji, len(animated_emojis))),
                        key=lambda e: e.name
                        )
                    ) if animated_emojis else 'Guild does not have any'
            )
        else:
            e.add_field(
                name='emojis', value='I have no permission to show external emojis', inline=False)
        e.set_footer(text=guild.id)

        await ctx.send(embed=e)
