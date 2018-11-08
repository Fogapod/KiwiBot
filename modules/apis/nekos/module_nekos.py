from objects.modulebase import ModuleBase
from objects.paginators import UpdatingPaginator
from objects.permissions import PermissionEmbedLinks

from .nekos import SFW_IMG_TAGS, NSFW_IMG_TAGS, TAG_NAME_REPLACEMENTS, neko_api_image_request

import random
from itertools import zip_longest

from discord import Embed, Colour, DMChannel


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <tag>'
    short_doc = 'Nekos'
    long_doc = (
        'Powered by https://nekos.life api\n\n'
        'Subcommands:\n'
        '\tlist: shows list of available tags\n'
        '\tsfw:  sends random  sfw tag\n'
        '\tnsfw: sends random nsfw tag\n'
    )

    name = 'nekos'
    aliases = (name, 'neko')
    category = 'Services'
    min_args = 1
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **options):
        result = ''
        subcommand = args[1].lower()

        if subcommand == 'list':
            result = f'{"SFW": >11} | NSFW\n{"-" * 25}\n'
            result += '\n'.join(
                f'{x: >11} | {y}' for x, y in zip_longest(sorted(SFW_IMG_TAGS), sorted(NSFW_IMG_TAGS), fillvalue='')
            )
            return f'```\n{result}```'

        tag = None
        nsfw = False

        if subcommand in SFW_IMG_TAGS:
            tag = subcommand
        elif subcommand in NSFW_IMG_TAGS:
            tag = subcommand
            nsfw = True
        elif subcommand == 'sfw':
            tag = subcommand
        elif subcommand == 'nsfw':
            tag = subcommand
            nsfw = True
        else:
            return await self.on_doc_request(ctx)

        if ctx.is_nsfw < nsfw:
            return await self.on_nsfw_permission_denied(ctx)

        p = UpdatingPaginator(self.bot)
        await p.run(ctx, self.paginator_update_func, update_args=(tag, ))

    async def paginator_update_func(self, p, tag):
        if tag == 'sfw':
            tag = random.choice(SFW_IMG_TAGS)
        elif tag == 'nsfw':
            tag = random.choice(NSFW_IMG_TAGS)

        response = await neko_api_image_request(
            TAG_NAME_REPLACEMENTS.get(tag, tag))

        if response is not None:
            e = Embed(colour=Colour.gold(), title=f'Tag: {tag}', url=response['url'])
            e.set_image(url=response['url'])
            e.set_footer(text='Click on 🆕 reaction to get new image')
            return {'embed': e}
        else:
            return {'content': 'Problem with api response. Please try again later'}
