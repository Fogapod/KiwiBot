from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from discord import Embed, Colour

from .nekos import neko_api_request


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <quesrion>'
    short_doc = 'Ask a question (answer is not guaranteed)'
    long_doc = ('Became possible with the use of https://nekos.life')

    name = 'why'
    aliases = (name, )
    category = 'Services'
    min_args = 1
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **options):
        question = args[1:]
        if question.endswith('?'):
            question = question[:-1]
        if len(question) > 251:
            question = question[:248] + '...'
        question = question[:1].lower() + question[1:] if question else ''

        e = Embed(colour=Colour.gold())
        if question:
            e.title = f'Why {question}?'
        response = await neko_api_request('why')
        if not response:
            return '{error} Problem with api response. Please, try again later'

        e.description = response['why']
        e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=e)