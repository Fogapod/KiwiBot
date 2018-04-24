from objects.modulebase import ModuleBase

from utils.funcs import find_channel

from discord.abc import PrivateChannel
from discord import Embed, Colour, TextChannel, VoiceChannel



class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [channel]'
    short_doc = 'Get information about given channel.'

    name = 'channel'
    aliases = (name, 'channelinfo')

    async def on_call(self, msg, args, **flags):
        if len(args) == 1:
            channel = msg.channel
        else:
            channel = await find_channel(
                args[1:], msg.guild, self.bot, global_id_search=True)

        if channel is None:
            return '{warning} Channel not found'

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
            additional_fields = [
                {
                    'name': 'Pins',
                    'value': len(await channel.pins())
                },
                {
                    'name': 'Category',
                    'value': channel.category.name
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
                }
            ]
        else:
            c_type = 'Category'
            member_count = msg.guild.member_count
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

        await self.send(msg, embed=e)