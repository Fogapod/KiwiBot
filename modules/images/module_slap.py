from objects.modulebase import ModuleBase

import io

import discord

from PIL import Image

from utils.funcs import find_image


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [image]'
    short_doc = 'Makes a slap meme'

    name = 'slap'
    aliases = (name, )
    category = 'Images'
    ratelimit = (1, 3)

    async def on_call(self, ctx, args, **flags):
        image = await find_image(args[1:], ctx, include_gif=False)
        if not image:
            return await ctx.warn('Give me an image to slap')

        source = Image.open(io.BytesIO(image))
        s_w, s_h = source.size
        if s_w + s_h > 10000:
            return await ctx.error('Input image is too big')

        template = Image.open('templates/slap')
        t_w, t_h = template.size

        resized = source.resize((280, 280), Image.ANTIALIAS)
        channels = resized.split()
        mask = channels[3] if len(channels) >= 4 else None

        template.paste(resized, (200, 310), mask=mask)

        result = io.BytesIO()
        template.save(result, format='PNG')

        await ctx.send(file=discord.File(result.getvalue(), filename=f'slap.png'))
