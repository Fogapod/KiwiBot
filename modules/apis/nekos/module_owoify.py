from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from discord import Embed, Colour

from .nekos import neko_api_request


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Make text kawaii'
    long_doc = ('Became possible with the use of https://nekos.life')

    name = 'owoify'
    aliases = (name, 'owo')
    category = 'Services'
    min_args = 1
    bot_perms = (PermissionEmbedLinks(), )

    async def on_not_enough_arguments(self, ctx):
        return '{warning} Pwease, gib me text to make it kawaii'

    async def on_call(self, ctx, args, **options):
        text = args[1:]
        if len(text) > 1000:
            return '{error} oopsie whoopsie, seems like youw text is longew thany 1000 symbols~~'

        chunks = [text[i:i + 200] for i in range(0, len(text), 200)]
        owo = ''
        for c in chunks:
            data = { 'text': c }
            response = await neko_api_request('owoify', **data)
            if response is None:
                break
            owo += response['owo']
        if not owo:
            return '{error} Problem with api response. Please, try again later'

        title = await neko_api_request('cat')
        e = Embed(colour=Colour.gold(), title=title.get('cat', None) or 'OwO')
        e.add_field(name=f'{ctx.author.display_name} just said...', value=owo)
        e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=e)
