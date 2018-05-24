from objects.bot import KiwiBot

import random


API_URL = 'https://nekos.life/api/v2'

SFW_IMG_TAGS = [
    'fox_girl', 'lizard', 'meow', 'neko', 'avatar', 'holo', 'wallpaper',
    'gasm', 'ngif','kemonomimi', 'eron'
]

NSFW_IMG_TAGS = [
    'hentai_gif', 'anal', 'bj', 'boobs', 'classic', 'cum', 'kuni',
    'les', 'lewd', 'nsfw_neko_gif', 'pussy', 'nsfw_avatar', 'tits',
    'smallboobs', 'femdom', 'pussy_jpg', 'keta', 'cum_jpg', 'hololewd',
    'yuri', 'lewdkemo', 'solog', 'lewdk', 'solo', 'feetg', 'erokemo',
    'hentai', 'blowjob', 'holoero', 'pwankg', 'ero', 'feet', 'eroyuri',
    'erofeet', 'erok'
]

TAG_NAME_REPLACEMENTS = {
    'nsfw_gif':   'nsfw_neko_gif',
    'hentai_gif': 'Random_hentai_gif'
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