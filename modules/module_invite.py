from modules.modulebase import ModuleBase

from permissions import PermissionEmbedLinks
from discord import Colour, Embed


DISCORD_AUTH_URL = 'https://discordapp.com/oauth2/authorize?client_id={id}&scope=bot&permissions={perms}'

class Module(ModuleBase):
    
    short_doc = 'Get bot invite link.'

    name = 'invite'
    aliases = (name, )
    required_perms = (PermissionEmbedLinks, )

    async def on_call(self, msg, *args, **options):
        e = Embed(
            title='TitleMyTitle', colour=Colour.gold(),
            description='Here are some useful links for you'
        )
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.add_field(
            name='Invite me to your guild',
            value='   |   '.join((
                '[admin](' + DISCORD_AUTH_URL.format(id=self.bot.user.id, perms=8) + ')',
                '[no admin](' + DISCORD_AUTH_URL.format(id=self.bot.user.id, perms=2146958583) + ')'
            )), inline=False
        )
        e.add_field(name='Contact developar', value='[development server](https://discord.gg/TNXn8R7)')

        await self.send(msg, embed=e)