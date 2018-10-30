from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks
from objects.paginators import Paginator

from discord import Embed, Colour

import aiohttp
import random

from bs4 import BeautifulSoup


BASE_URL = 'https://www.google.com/search?'

USERAGENTS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'

)

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <query>'
    short_doc = 'Search for images on google'

    name = 'img'
    aliases = (name, 'image')
    category = 'Services'
    bot_perms = (PermissionEmbedLinks(), )
    min_args = 1
    ratelimit = (1, 5)

    async def on_call(self, ctx, args, **flags):
        query = args[1:]

        params = {
            'q': query,
            'tbm': 'isch',
            'safe': 'off' if ctx.is_nsfw else 'strict'
        }

        headers = {'User-Agent': random.choice(USERAGENTS)}
        proxy = random.choice([None] + list(self.bot.proxies.keys()))

        async with self.bot.sess.get(BASE_URL, params=params, headers=headers, proxy=proxy) as r:
            if r.status != 200:
                return await ctx.error(f'Rquest failed: {r.status}')

            soup = BeautifulSoup(await r.text(), 'html.parser')


        candidates = soup('img', class_='rg_ic rg_i')
        urls = list(filter(None, [i.get('data-src') for i in candidates]))

        if len(urls) == 0:
            return await ctx.warn('No results found')

        p = Paginator(self.bot)

        def make_embed(page, url):
            e = Embed(colour=Colour.gold(), title=query[:128])
            e.set_author(
                name='\u200b', icon_url='https://www.google.com/s2/favicons?domain=www.google.com')
            e.set_image(url=url)
            e.set_footer(
                text=f'Page {page} / {len(urls)}',
                icon_url=ctx.author.avatar_url
            )
            return e

        for i, url in enumerate(urls):
            p.add_page(embed=make_embed(i + 1, url))

        await p.run(ctx)
