from objects.bot import KiwiBot

import random


API_URL = 'https://nekos.life/api/v2'

SFW_IMG_TAGS = [
    'fox', 'lizard', 'meow', 'neko', 'avatar', 'holo',
    'ngif','kemonomimi', 'eron', 'waifu', 'woof', 'goose'
]

NSFW_IMG_TAGS = [
    'hentaig', 'anal', 'bj', 'boobs', 'classic', 'cumg', 'kuni',
    'les', 'lewd', 'nsfwg', 'pussy', 'pussyg', 'nsfw_avatar',
    'tits', 'smallboobs', 'femdom', 'keta', 'cum', 'hololewd',
    'yuri', 'lewdkemo', 'solog', 'lewdk', 'solo', 'feetg', 'erokemo',
    'hentai', 'blowjob', 'holoero', 'pwankg', 'ero', 'feet', 'eroyuri',
    'erofeet', 'erok', 'wallpaper', 'gasm'
]

TAG_NAME_REPLACEMENTS = {
    'fox':     'fox_girl',
    'cum':     'cum_jpg',
    'cumg':    'cum',
    'nsfwg':   'nsfw_gif',
    'pussy':   'pussy_jpg',
    'nsfwg':   'nsfw_neko_gif',
    'pussyg':  'pussy',
    'hentaig': 'Random_hentai_gif'
}

# actions
# 'cuddle', 'feed', 'hug', 'kiss', 'pat', 'poke', 'slap', 'tickle'

bot = KiwiBot.get_bot()


async def neko_api_image_request(tag, **params):
    return await neko_api_request(f'img/{tag}', **params)

async def neko_api_request(endpoint, **params):
    async with bot.sess.get('/'.join((API_URL, endpoint)), params=params) as r:
        if r.status == 200:
            result_json = await r.json()
            return result_json
        else:
            return None
