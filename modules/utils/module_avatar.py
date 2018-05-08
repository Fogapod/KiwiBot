from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from utils.funcs import find_user

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [user]'
    short_doc = 'Get user avatar'

    name = 'avatar'
    aliases = (name, 'pfp')
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, msg, args, **flags):
        if len(args) == 1:
            user = msg.author
        else:
            user = await find_user(args[1:], msg, self.bot)

        if user is None:
            return '{warning} User not found'

        formats = ['png', 'webp', 'jpg']
        if user.is_avatar_animated():
            formats.insert(0, 'gif')

        e = Embed(
            colour=Colour.gold(),
            description=' | '.join(f'[{f}]({user.avatar_url_as(format=f)})' for f in formats)
        )
        e.set_image(url=user.avatar_url_as(static_format='png'))
        e.set_footer(text=user)

        await self.send(msg, embed=e)