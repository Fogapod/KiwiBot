from objects.modulebase import ModuleBase
from objects.paginators import UpdatingPaginator
from objects.permissions import (
    PermissionEmbedLinks, PermissionAddReactions, PermissionReadMessageHistory)


from discord import Embed, Colour


API_URL = 'http://inspirobot.me/api?generate=true'

class Module(ModuleBase):

    short_doc = 'Very inspirational.'

    name = 'inspire'
    aliases = (name, 'inspirebot')
    required_perms = (
        PermissionEmbedLinks(), PermissionAddReactions(),
        PermissionReadMessageHistory()
    )

    async def on_call(self, msg, args, **options):
        p = UpdatingPaginator(self.bot)
        await p.run(
            msg.channel, self.paginator_update_func, ((), {}),
            target_user=msg.author
        )

    async def paginator_update_func(self):
        async with self.bot.sess.get(API_URL) as r:
            if r.status == 200:
                url = await r.text()
                e = Embed(colour=Colour.gold())
                e.set_image(url=url)
                e.set_footer(text='Powered by https://inspirebot.me')
                return { 'embed': e }