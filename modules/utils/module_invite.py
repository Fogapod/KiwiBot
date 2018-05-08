from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from constants import BOT_OWNER_ID, DEV_GUILD_INVITE

from discord import Colour, Embed, NotFound


DISCORD_AUTH_URL = 'https://discordapp.com/oauth2/authorize?client_id={id}&scope=bot&permissions={perms}'

class Module(ModuleBase):
    
    short_doc = 'Get bot invite link'

    name = 'invite'
    aliases = (name, )
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, msg, args, **flags):
        e = Embed(
            title='My invite links', colour=Colour.gold(),
            description='   |   '.join((
                '[admin](' + DISCORD_AUTH_URL.format(id=self.bot.user.id, perms=8) + ')',
                '[no admin](' + DISCORD_AUTH_URL.format(id=self.bot.user.id, perms=2146958583) + ')'
            ))
        )
        owner = self.bot.get_user(BOT_OWNER_ID)
        if owner is None:
            try:
                owner = await self.bot.get_user_info(BOT_OWNER_ID)
            except NotFound:
                pass

        e.add_field(
            name='Contact developar',
            value=(
                f'Feel free to contact owner: **{owner}** [**{BOT_OWNER_ID}**]\n'
                f'[development server]({DEV_GUILD_INVITE})'
            )
        )

        await self.send(msg, embed=e)