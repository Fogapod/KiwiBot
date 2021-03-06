from objects.modulebase import ModuleBase

import discord

from io import BytesIO

from PIL import Image
from PIL.ImageOps import mirror

from utils.funcs import find_image


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
        robin = await image.to_pil_image()
        if image.error:
            return await ctx.warn(f'Error getting first image: {image.error}')

        batface_flag = flags.get('batface')
        if batface_flag is not None:
            image = await find_image(batface_flag, ctx, include_gif=False)
            bat = await image.to_pil_image()
            if image.error:
                return await ctx.warn(f'Error getting second image: {image.error}')
        else:
            try:
                bat = Image.open(
                    BytesIO(
                        await ctx.author.avatar_url_as(format='png').read()
                    )
                )
            except Exception as e:
                return await ctx.error(f'Failed to download author\'s avatar: {e}')

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

        result = BytesIO()
        template.save(result, format='PNG')

        template.close()
        bat.close()
        robin.close()

        return BytesIO(result.getvalue())
