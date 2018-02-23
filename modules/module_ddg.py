from modules.modulebase import ModuleBase

from utils.formatters import format_response
from utils.helpers import get_string_after_entry

from discord import File

from aiohttp import ClientSession


API_URL = 'https://api.duckduckgo.com'

class Module(ModuleBase):
    """{prefix}{keywords} <text>

    Web search using duckduckgo.
    {protection} or higher permission level required to use"""

    name = 'ddg'
    keywords = (name, 'duckduckgo')
    arguments_required = 1
    protection = 0

    async def on_call(self, msg, *args, **options):
        params = {
            'q': get_string_after_entry(args[0], msg.content),
            'o': 'json'
        }

        async with ClientSession() as s:
            async with s.get(API_URL, params=params) as r:
                if r.status != 200:
                    return '{error} request failed: ' + str(r.status)
                r_json = await r.json(content_type='application/x-javascript')
            
            result = r_json['AbstractText']

            if not result:
                return 'Nothing found'
            else:
                image_url = r_json['Image']

            image = None
            if image_url:
                async with s.get(image_url) as r:
                    if r.status == 200:
                        image = File(await r.read(), filename='file.png')
                    else:
                        result += '{error} failed to fetch image: ' + image_url

        result = await format_response(result, msg, self.bot)
        await self.bot.send_message(msg, result, file=image, response_to=msg)                     