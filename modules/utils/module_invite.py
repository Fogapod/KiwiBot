from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from constants import DEV_GUILD_INVITE

from discord import Colour, Embed, NotFound


DISCORD_AUTH_URL = 'https://discordapp.com/oauth2/authorize?client_id={id}&scope=bot&permissions={perms}'

class Module(ModuleBase):
    
    short_doc = 'Returns bot invite link'

    name = 'invite'
    aliases = (name, )
    category = 'Bot'
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **flags):
        e = Embed(
            title='My invite links', colour=Colour.gold(),
            description='   |   '.join((
                f'[admin]({DISCORD_AUTH_URL.format(id=self.bot.user.id, perms=8)})',
                f'[all perms]({DISCORD_AUTH_URL.format(id=self.bot.user.id, perms=2146958583)})',
                f'[no perms]({DISCORD_AUTH_URL.format(id=self.bot.user.id, perms=0)})'
            ))
        )

        e.add_field(
            name='Contact developar',
            value=(
                f'Feel free to contact owner: **{self.bot.owner}** [**{self.bot.owner.id}**]\n'
                f'[development server]({DEV_GUILD_INVITE})'
            )
        )

        await ctx.send(embed=e)
