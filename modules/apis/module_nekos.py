from objects.modulebase import ModuleBase
from objects.paginators import UpdatingPaginator
from objects.permissions import PermissionEmbedLinks, PermissionReadMessageHistory

from itertools import zip_longest

import random

from discord import Embed, Colour, DMChannel


API_URL = 'https://nekos.life/api/v2'

SFW_IMG_TAGS = [
    'cuddle', 'feed', 'fox_girl', 'hug', 'kiss', 'lizard', 'meow', 'neko',
    'pat', 'poke', 'slap', 'tickle', 'avatar'
]
NSFW_IMG_TAGS = [
    'random_hentai_gif', 'anal', 'bj', 'boobs', 'classic', 'cum', 'kuni',
    'les', 'lewd', 'nsfw_neko_gif', 'pussy', 'nsfw_avatar'
]


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <tag|subcommand>'
    short_doc = 'Nekos'
    long_doc = (
        'Powered by https://nekos.life api\n\n'
        'Subcommands:\n'
        '\tlist: show list available image tags'
        '\n\tsfw: random sfw image tag'
        '\n\tnsfw: random nsfw image tag'
        '\n\towoify: make your sentence kawaii'
        '\n\twhy: ask a question (answer is not guaranteed)'
    )

    name = 'nekos'
    aliases = (name, 'neko')
    category = 'Services'
    min_args = 1
    bot_perms = (PermissionEmbedLinks(), PermissionReadMessageHistory())

    async def on_call(self, ctx, args, **options):
        result = ''
        subcommand = args[1].lower()

        if subcommand == 'list':
            result = 'SFW           NSFW\n'
            result += '\n'.join(
                f'{x:<14}{y}' for x, y in zip_longest(SFW_IMG_TAGS, NSFW_IMG_TAGS, fillvalue='')
            )
            return f'```\n{result}```'

        image_tag = None
        nsfw = False

        if subcommand in SFW_IMG_TAGS:
            image_tag = subcommand
        elif subcommand in NSFW_IMG_TAGS:
            image_tag = subcommand
            nsfw = True
        elif subcommand == 'sfw':
            image_tag = random.choice(SFW_IMG_TAGS)
        elif subcommand == 'nsfw':
            image_tag = random.choice(NSFW_IMG_TAGS)
            nsfw = True
        elif subcommand == 'owoify':
            if len(args) < 3:
                return '{warning} Pwease, give me text to make kawaii'
            text = args[2:]
            if len(text) > 1000:
                return '{error} oopsie whoopsie, seems like youw text is longew thany 1000 chaws~~'
            chunks = [text[i:i + 200] for i in range(0, len(text), 200)]
            owo = ''
            url = '/'.join((API_URL, 'owoify'))
            for c in chunks:
                data = { 'text': c }
                response = await self.do_request(url, **data)
                if response is None:
                    owo = ''
                    break
                owo += response['owo']
            if owo:
                title = await self.do_request('/'.join([API_URL, 'cat']))
                e = Embed(
                    colour=Colour.gold(), title=title.get('cat', None) or 'OwO')
                e.add_field(
                    name=f'{ctx.author.display_name} just said...',
                    value=owo
                )
                e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

                return await ctx.send(embed=e)
        elif subcommand == 'why':
            question = args[2:]
            if question.endswith('?'):
                question = question[:-1]
            if len(question) > 251:
                return '{error} Your question is too long...'

            e = Embed(colour=Colour.gold())
            if question:
                e.title = f'why {question}?'
            url = '/'.join((API_URL, 'why'))
            response = await self.do_request(url)
            if response is not None:
                e.description = response['why']
                e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

                return await ctx.send(embed=e)
        else:
            return await self.on_doc_request(ctx)

        if getattr(ctx.channel, 'is_nsfw', lambda: isinstance(ctx.channel, DMChannel))() < nsfw:
            return await self.on_nsfw_permission_denied(ctx)

        if image_tag:
            if image_tag == 'random_hentai_gif':
                image_tag = 'Random_hentai_gif'
            url = '/'.join((API_URL, 'img', image_tag))

            p = UpdatingPaginator(self.bot)
            return await p.run(
                ctx, self.paginator_update_func, update_args=(url, image_tag))

        return '{error} Problem with api response. Please, try again later'

    async def paginator_update_func(self, url, image_tag):
        response = await self.do_request(url)
        if response is not None:
            e = Embed(
                colour=Colour.gold(), title=image_tag, url=response['url']
            )
            e.set_image(url=response['url'])
            return { 'embed': e }

    async def do_request(self, url, **params):
        async with self.bot.sess.get(url, params=params) as r:
            if r.status == 200:
                result_json = await r.json()
                return result_json
            else:
                return None