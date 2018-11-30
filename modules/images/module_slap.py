from objects.modulebase import ModuleBase

import io

import discord

from PIL import Image
from PIL.ImageOps import mirror

from utils.funcs import find_image


MAX_SIZE = 10000

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [image]'
    short_doc = 'Makes a slap meme'
    long_doc = (
        'Flags:\n'
        '\t[--batface|-b] <image>: uses custom second image'
    )

    name = 'slap'
    aliases = (name, )
    category = 'Images'
    flags = {
        'batface': {
            'alias': 'b',
            'bool': False
        }
    }
    ratelimit = (1, 3)

    async def on_call(self, ctx, args, **flags):
        image = await find_image(args[1:], ctx, include_gif=False)
        await image.ensure()
        if image.error:
            return await ctx.warn(f'Error downloading first image: {image.error}')

        robin = image.bytes

        batface_flag = flags.get('batface')
        if batface_flag is not None:
            image = await find_image(batface_flag, ctx, include_gif=False)
            await image.ensure()
            if image.error:
                return await ctx.warn(
                    f'Error finding second image: {image.error}'
                )

            bat = image.bytes
        else:
            try:
                async with self.bot.sess.get(
                        ctx.author.avatar_url_as(format='png'), raise_for_status=True) as r:
                    bat = await r.read()
            except Exception:
                return await ctx.error('Failed to download author\'s avatar')

        robin = Image.open(io.BytesIO(robin))
        if sum(robin.size) > MAX_SIZE:
            return await ctx.error('First image is too big')

        bat = Image.open(io.BytesIO(bat))
        if sum(bat.size) > MAX_SIZE:
            return await ctx.error('Second image is too big')

        result = await self.bot.loop.run_in_executor(
            None, self.slap, robin, bat)

        await ctx.send(file=discord.File(result, filename=f'slap.png'))

    def slap(self, robin, bat):
        template = Image.open('templates/slap.png')

        bat = bat.convert('RGBA')
        bat = mirror(bat.resize((220, 220), Image.ANTIALIAS).rotate(10, expand=True))

        template.paste(bat, (460, 200), mask=bat.split()[3])

        robin = robin.convert('RGBA')
        robin = robin.resize((260, 260), Image.ANTIALIAS)

        template.paste(robin, (200, 310), mask=robin.split()[3])

        result = io.BytesIO()
        template.save(result, format='PNG')

        return result.getvalue()
