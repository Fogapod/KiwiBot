from objects.modulebase import ModuleBase

from utils.funcs import find_image


API_URL = 'https://api.tsu.sh/google/ocr'

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [image]'
    short_doc = 'Optical Character Recognition'

    name = 'ocr'
    aliases = (name, )
    category = 'Services'
    ratelimit = (1, 5)

    async def on_call(self, ctx, args, **options):
        image = await find_image(args[1:], ctx, include_gif=False)
        if image.error:
            return await ctx.warn(f'Error getting image: {image.error}')

        async with ctx.session.get(API_URL, params=dict(q=image.url)) as r:
            if r.status != 200:
                if r.content_type.lower() != 'application/json':
                    # something went terribly wrong
                    return await ctx.error(
                        f'Something really bad happened with underlying API: {r.status}'
                    )

                try:
                    json = await r.json()
                except json.JSONDecodeError:
                    return await ctx.error(
                        'Unable to process response from API'
                    )

                return await ctx.error(
                    f'Error in underlying API[{r.status}]: '
                    f'{json.get("message", "[MISSING]")}'
                )

            json = await r.json()

        text = json['text']
        if not text:
            return await ctx.warn('Unable to find text')

        return f'```\n{text}```'
