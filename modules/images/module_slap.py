from objects.modulebase import ModuleBase

import io

import discord

from PIL import Image
from PIL.ImageOps import mirror

from utils.funcs import find_image


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [image]'
    short_doc = 'Makes a slap meme'
    long_doc = (
        'Flags:\n'
        '\t[--avatar|-a]: don\'t place author avatar on Batman\'s face if added'
    )

    name = 'slap'
    aliases = (name, )
    category = 'Images'
    flags = {
        'avatar': {
            'alias': 'a',
            'bool': True
        }
    }
    ratelimit = (1, 3)

    async def on_call(self, ctx, args, **flags):
        image = await find_image(args[1:], ctx, include_gif=False)
        await image.ensure()
        if image.error:
            return await ctx.warn(image.error)

        source = Image.open(io.BytesIO(image.bytes))
        if sum(source.size) > 10000:
            return await ctx.error('Input image is too big')

        if flags.get('avatar', False):
            author_source = None
        else:
            try:
                async with self.bot.sess.get(
                        ctx.author.avatar_url_as(format='png'), raise_for_status=True) as r:
                    author_source = Image.open(io.BytesIO(await r.read()))
            except Exception:
                return await ctx.error(
                    'Failed to download author avatar, use **--avatar** flag to disable it')

        template = Image.open('templates/slap')

        if author_source is not None:
            author_resized = author_source.resize((240, 240), Image.ANTIALIAS)
            author_flipped = mirror(author_resized)
            author_channels = author_flipped.split()
            author_mask = author_channels[3] if len(author_channels) >= 4 else None

            template.paste(author_flipped, (480, 200), mask=author_mask)

        resized = source.resize((280, 280), Image.ANTIALIAS)
        channels = resized.split()
        mask = channels[3] if len(channels) >= 4 else None

        template.paste(resized, (200, 310), mask=mask)

        result = io.BytesIO()
        template.save(result, format='PNG')

        await ctx.send(file=discord.File(result.getvalue(), filename=f'slap.png'))
