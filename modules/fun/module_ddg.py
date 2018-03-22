from objects.modulebase import ModuleBase

from discord import File

from aiohttp import ClientSession

import random


API_URL = 'https://api.duckduckgo.com'

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <query>'
    short_doc = 'Web search using duckduckgo.'

    name = 'ddg'
    aliases = (name, 'duckduckgo')
    arguments_required = 1
    protection = 0

    async def on_call(self, msg, *args, **options):
        params = {
            'q': msg.content.partition(args[0])[2].lstrip(),
            'o': 'json'
        }

        async with ClientSession() as s:
            async with s.get(API_URL, params=params) as r:
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
                async with s.get(image_url) as r:
                    if r.status == 200:
                        image = File(await r.read(), filename=image_url.split('/')[-1])
                    else:
                        result += '{error} failed to fetch image: ' + image_url

        await self.send(msg, content=abstract_text, file=image)