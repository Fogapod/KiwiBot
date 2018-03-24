from objects.modulebase import ModuleBase

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = ''
    short_doc = 'Handler for guild add/remove events.'

    name = 'guild-add-remove'
    hidden = True

    async def on_load(self, from_reload):
        if from_reload:
            return

        self.events = {
            'guild_join':   self.on_guild_join,
            'guild_remove': self.on_guild_remove
        }

        self.log_channel = self.bot.get_channel(424492773215961090)

    async def on_guild_join(self, guild):
        e = self.get_guild_info(guild)
        e.title = f'Added to guild {guild}'
        await self.log_channel.send(embed=e)

    async def on_guild_remove(self, guild):
        e = self.get_guild_info(guild)
        e.title = f'Removed from guild {guild}'
        await self.log_channel.send(embed=e)

    def get_guild_info(self, guild):
        e = Embed(colour=Colour.gold())
        e.add_field(name='guild id', value=guild.id)
        bot_count = sum(1 for m in guild.members if m.bot)
        bot_ratio = round(bot_count / guild.member_count * 100)
        e.add_field(name='members', value=f'{guild.member_count - bot_count} + {bot_count} bots')
        e.add_field(name='owner id', value=guild.owner.id)
        e.add_field(name='bot ratio', value=f'{bot_ratio}%')
        e.add_field(name='total guilds', value=len(self.bot.guilds))
        e.set_thumbnail(url=guild.icon_url or guild.owner.avatar_url)
        e.set_footer(text=guild.owner, icon_url=guild.owner.avatar_url)

        return e