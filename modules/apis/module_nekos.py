from objects.modulebase import ModuleBase

from itertools import zip_longest

import random

from discord import Embed, Colour


API_URL = 'https://nekos.life/api/v2'

SFW_IMG_TAGS = [
    'cuddle', 'feed', 'fox_girl', 'hug', 'kiss', 'lizard', 'meow', 'neko',
     'pat', 'poke', 'slap', 'tickle'
]
NSFW_IMG_TAGS = [
    'random_hentai_gif', 'anal', 'bj', 'boobs', 'classic', 'cum', 'kuni',
    'les', 'lewd', 'nsfw_neko_gif', 'pussy'
]


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <tag|subcommand>'
    short_doc = 'Nekos.'
    additional_doc = (
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
    required_args = 1

    async def on_call(self, msg, args, **options):
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
                return '{warning} Please, provide text to owoify'
            text = args[2:]
            if len(text) > 100:
                return '{error} oopsie whoopsie, seems like your text is longer than 100 chars~~'

            url = '/'.join((API_URL, 'owoify'))
            data = { 'text': text }
            response = await self.do_request(url, **data)
            e = Embed(colour=Colour.gold(), title='OwO')
            e.add_field(
                name=f'{msg.author.display_name} just said...',
                value=response['owo']
            )
            e.set_footer(text=msg.author, icon_url=msg.author.avatar_url)

            await self.send(msg, embed=e)
            return
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
            e.description = response['why']
            e.set_footer(text=msg.author, icon_url=msg.author.avatar_url)

            await self.send(msg, embed=e)
            return
        else:
            return await self.on_doc_request(msg)

        if nsfw and not msg.channel.nsfw:
            return await self.on_nsfw_permission_denied(msg)

        if image_tag:
            if image_tag == 'random_hentai_gif':
                image_tag = 'Random_hentai_gif'
            url = '/'.join((API_URL, 'img', image_tag))
            response = await self.do_request(url)
            if response is not None:
                e = Embed(
                    colour=Colour.gold(), title=image_tag, url=response['url']
                )
                e.set_image(url=response['url'])
                await self.send(msg, embed=e)
                return

        return '{error} Problem with api response. Please, try again later'

    async def do_request(self, url, **params):
        async with self.bot.sess.get(url, params=params) as r:
            if r.status == 200:
                result_json = await r.json()
                return result_json
            else:
                return ''