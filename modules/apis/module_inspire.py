from objects.modulebase import ModuleBase
from objects.paginators import UpdatingPaginator
from objects.permissions import PermissionEmbedLinks


from discord import Embed, Colour


API_URL = 'http://inspirobot.me/api?generate=true'

class Module(ModuleBase):

    short_doc = 'Very inspirational'

    name = 'inspire'
    aliases = (name, 'inspirebot')
    category = 'Services'
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **options):
        p = UpdatingPaginator(self.bot)
        await p.run(ctx, self.paginator_update_func)

    async def paginator_update_func(self):
        async with self.bot.sess.get(API_URL) as r:
            if r.status == 200:
                e = Embed(colour=Colour.gold())
                e.set_image(url=await r.text())
                e.set_footer(text='Powered by https://inspirobot.me')

                return { 'embed': e }