from objects.modulebase import ModuleBase

from discord import File

from aiohttp import ClientSession

import random


API_URL = 'https://api.duckduckgo.com'

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <query>'
    short_doc = 'Web search using duckduckgo'

    name = 'ddg'
    aliases = (name, 'duckduckgo')
    min_args = 1

    async def on_call(self, msg, args, **flags):
        params = {
            'q': args[1:],
            'o': 'json'
        }

        async with self.bot.sess.get(API_URL, params=params) as r:
            if r.status != 200:
                return '{error} request failed: ' + str(r.status)
            r_json = await r.json(content_type='application/x-javascript')

        abstract_text = r_json['AbstractText']

        if not abstract_text:
            related = r_json['RelatedTopics']
            if not related:
                return '{warning} Nothing found'
            topic = random.choice(related)
            if 'Topics' in topic:
                topic = random.choice(topic['Topics'])
            abstract_text = topic['Text']
            image_url = topic['Icon']['URL']
        else:
            image_url = r_json['Image']

        image = None
        if image_url:
            async with self.bot.sess.get(image_url) as r:
                if r.status == 200:
                    image = File(await r.read(), filename=image_url.split('/')[-1])
                else:
                    result += '{error} failed to fetch image: ' + image_url

        await self.send(msg, abstract_text, file=image)