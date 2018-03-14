from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from utils.funcs import find_user

from discord import Embed


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [user]'
    short_doc = 'Get user avatar.'

    name = 'avatar'
    aliases = (name, 'pfp')
    required_perms = (PermissionEmbedLinks, )

    async def on_call(self, msg, *args, **flags):
        format = flags.pop('format', 'png')

        if len(args) == 1:
            user = msg.author
        else:
            user = await find_user(
                msg.content.partition(args[0])[2].lstrip(),
                msg, self.bot
            )

        if user is None:
            return '{warning} User not found'

        avatar_url = user.avatar_url_as(static_format=format)

        e = Embed(title=f'{user.id}', url=avatar_url)
        e.set_image(url=avatar_url)
        e.set_footer(text=user)

        await self.send(msg, embed=e)