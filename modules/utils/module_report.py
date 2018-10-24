from objects.modulebase import ModuleBase

from constants import REPORT_CHANNEL_ID, DEV_GUILD_ID

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <problem>'
    short_doc = 'Report problem/send suggestion'

    name = 'report'
    aliases = (name, )
    category = 'Actions'
    min_args = 1
    ratelimit = (1, 60)

    async def on_load(self, from_reload):
        self.report_channel = self.bot.get_channel(REPORT_CHANNEL_ID)

    async def on_call(self, ctx, args, **flags):
        e = Embed(
            colour=Colour.gold(), description=args[1:],
            title=f'Report from {"guild " + ctx.guild.name if ctx.guild else "direct messages"}'
        )
        if ctx.guild:
            e.add_field(name='Guild id', value=ctx.guild.id)
            e.add_field(name='Channel', value=f'{ctx.channel} {ctx.channel.id}')
        e.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        e.set_footer(text=f'Author id: {ctx.author.id}')

        await ctx.send(channel=self.report_channel, embed=e, register=False)

        return f'Sent report to {self.report_channel.guild.name}'
