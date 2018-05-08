from objects.modulebase import ModuleBase

from constants import REPORT_CHANNEL_ID, DEV_GUILD_ID

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <problem>'
    short_doc = 'Report problem/send suggestion'

    name = 'report'
    aliases = (name, )
    min_args = 1

    async def on_load(self, from_reload):
        self.report_channel = self.bot.get_channel(REPORT_CHANNEL_ID)

    async def on_call(self, msg, args, **flags):
        e = Embed(
            colour=Colour.gold(), description=args[1:],
            title=f'Report from {"guild " + msg.guild.name if msg.guild else "direct messages"}'
        )
        if msg.guild:
            e.add_field(name='Guild id', value=msg.guild.id)
            e.add_field(name='Channel', value=f'{msg.channel} {msg.channel.id}')
        e.set_author(name=msg.author, icon_url=msg.author.avatar_url)
        e.set_footer(text=f'Author id: {msg.author.id}')

        await self.bot.send_message(self.report_channel, embed=e)
        return f'Sent report to {self.report_channel.guild.name}'