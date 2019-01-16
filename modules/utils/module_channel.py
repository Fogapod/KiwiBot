from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from utils.funcs import find_channel

from discord.abc import PrivateChannel
from discord import Embed, Colour, TextChannel, VoiceChannel


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [channel]'
    short_doc = 'Get information about given channel'

    name = 'channel'
    aliases = (name, 'channelinfo')
    category = 'Discord'
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **flags):
        if len(args) == 1:
            channel = ctx.channel
        else:
            channel = await find_channel(
                args[1:], ctx.guild, global_id_search=True)

        if channel is None:
            return await ctx.warn('Channel not found')

        e = Embed(colour=Colour.gold(), title=getattr(channel, 'name', 'DM Channel'))
        additional_fields = []

        if isinstance(channel, PrivateChannel):
            c_type = 'DM Channel'
            member_count = 2
            additional_fields.append(
                {
                    'name': 'pins',
                    'value': len(await channel.pins())
                },
            )
        elif isinstance(channel, TextChannel):
            c_type = 'Text Channel'
            member_count = len(channel.members)
            if channel.permissions_for(channel.guild.me).read_messages:
                pins = len(await channel.pins())
            else:
                pins = 'No access'

            additional_fields = [
                {
                    'name': 'Pins',
                    'value': pins
                },
                {
                    'name': 'Category',
                    'value': channel.category.name if channel.category else 'No category'
                },
                {
                    'name': 'NSFW',
                    'value': channel.is_nsfw()
                },
                {
                    'name': 'Topic',
                    'value': channel.topic or 'Empty',
                    'inline': False
                }
            ]
        elif isinstance(channel, VoiceChannel):
            c_type = 'Voice Channel'
            member_count = len(channel.members)
            additional_fields = [
                {
                    'name': 'User limit',
                    'value':channel.user_limit or 'No limit'
                },
                {
                    'name': 'Bitrate',
                    'value': channel.bitrate
                },
                {
                    'name': 'Category',
                    'value': channel.category.name if channel.category else 'No category'
                }
            ]
        else:
            c_type = 'Category'
            member_count = ctx.guild.member_count
            additional_fields = [
                {
                    'name': 'Channels',
                    'value': len(channel.channels)
                }
            ]

        e.add_field(name='Channel type', value=c_type)
        e.add_field(
            name='Created',
            value=f'`{channel.created_at.replace(microsecond=0)}`'
        )
        e.add_field(name='Member count', value=member_count)

        for field in additional_fields:
            e.add_field(**field)

        e.set_footer(text=channel.id)

        await ctx.send(embed=e)
