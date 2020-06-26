"""
NOTE: This monstrocity is a result of copying code from:
    - module_goodtranslotor2.py
    - module_ocr.py
    - module_slap.py

Ideally these should be baked into bot to avoid code duplication, alternatively better
module interaction could be achived. Unfortunantely KiwiBot is discontinued and none of
these will be implemented. Please see README.md for details.
"""

from objects.modulebase import ModuleBase

import json
import textwrap
import discord

from io import BytesIO

from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageOps

from utils.funcs import find_image


OCR_API_URL = 'https://api.tsu.sh/google/ocr'
TRANSLATE_API_URL = 'https://translate.yandex.net/api/v1.5/tr.json/'

# I have no idea why I have this font in my system, was 1st one I've found
# Docker image should have it
FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

PX_TO_PT_RATIO = 1.3333333

TRANSLATE_CAP = 6
BLUR_CAP = 40


class TextField:
    def __init__(self, full_text, padding=3):
        self.text = full_text

        self.left = None
        self.upper = None
        self.right = None
        self.lower = None

        self._padding = padding

    def merge(self, vertices):
        left, upper, right, lower = self._vertices_to_coords(vertices)

        self.left = left if self.left is None else min((self.left, left))
        self.upper = upper if self.upper is None else min((self.upper, upper))
        self.right = right if self.right is None else max((self.right, right))
        self.lower = lower if self.lower is None else max((self.lower, lower))

    @staticmethod
    def _vertices_to_coords(vertices):
        """Returns Pillow style coordinates (left, upper, right, lower)."""

        return (
            vertices[0].get("x", 0),
            vertices[0].get("y", 0),  # was missing from response once
            vertices[1]["x"],
            vertices[3]["y"],
        )

    @property
    def coords(self):
        return (self.left, self.upper, self.right, self.lower)

    @property
    def coords_padded(self):
        # TODO: make sure this doesnt segfault with wrong coords?? Thanks Pillow
        return (
            self.left - self._padding,
            self.upper - self._padding,
            self.right + self._padding,
            self.lower + self._padding
        )

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.lower - self.upper

    @property
    def font_size(self):
        # either ratio is wrong or I am doing something wrong, but I have to substitude
        # a constant value for this to work
        return max((1, round(PX_TO_PT_RATIO * self.height) - 5))

    @property
    def stroke_width(self):
        return max((1, round(self.font_size / 20)))



class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [image]'
    short_doc = 'Translates text on image'
    long_doc = (
        'Flags:\n'
        '\t[--language|-l] <language=\'en\'>: output language'
    )

    name = 'trocr'
    aliases = (name, )
    category = 'Images'
    flags = {
        'language': {
            'alias': 'l',
            'bool': False
        }
    }
    ratelimit = (1, 15)

    async def on_load(self, from_reload):
        # copied from module_goodtranslator2.py
        self.api_key = self.bot.config.get('yandex_api_key')
        if self.api_key:
            params = {
                'key': self.api_key,
                'ui': 'en'
            }

            async with self.bot.sess.get(TRANSLATE_API_URL + 'getLangs', params=params) as r:
                if r.status == 200:
                    self.langs = (await r.json())['langs']
                    return

        raise Exception('No yandex api key in config or key is invalid')

    async def translate(self, text, in_lang, out_lang):
        params = {
            'key': self.api_key,
            'text': text,
            'lang': f'{in_lang}-{out_lang}' if in_lang in self.langs else out_lang
        }

        try:
            async with self.bot.sess.post(TRANSLATE_API_URL + 'translate', params=params) as r:
                if r.status != 200:
                    return f"[HTTP {r.status}] Error"

                r_json = await r.json()
                return r_json['text'][0]
        except Exception:
            return "Error translating"

    async def on_call(self, ctx, args, **flags):
        if args[1:].lower() == 'list':
            return '\n'.join(f'`{k}`: {v}' for k, v in self.langs.items())

        image = await find_image(args[1:], ctx, include_gif=False)
        src = await image.to_pil_image()
        if image.error:
            return await ctx.warn(f'Error getting first image: {image.error}')

        lang_flag = flags.get('language', 'en')
        if lang_flag and lang_flag.lower() not in self.langs:
            return await ctx.warn('Invalid input language. Try using `list` subcommand')

        # everything below is copied from module_ocr.py
        async with ctx.session.get(OCR_API_URL, params=dict(q=image.url, raw=1)) as r:
            if r.status != 200:
                if r.content_type.lower() != 'application/json':
                    # something went terribly wrong
                    return await ctx.error(
                        f'Something really bad happened with underlying OCR API: {r.status}'
                    )

                try:
                    json = await r.json()
                except json.JSONDecodeError:
                    return await ctx.error(
                        'Unable to process response from OCR API'
                    )

                return await ctx.error(
                    f'Error in underlying OCR API[{r.status}]: '
                    f'{json.get("message", "[MISSING]")}'
                )
            json = await r.json()

        # everything above is copied from module_ocr.py

        text_data = json["responses"][0].get("textAnnotations")
        if not text_data:
            return await ctx.warn("No text detected")

        # Google OCR API returns entry for each word separately, but they can be joined
        # by checking full image description. In description words are combined into
        # blocks, blocks are separated by newlines, there is a trailing newline.
        # Coordinates from words in the same block can be merged
        current_word = 1 # 1st annotation is entire text
        translations_count = 0
        fields = []
        for line in text_data[0]["description"].split("\n")[:-1]:
            translated_line = line
            if translations_count < TRANSLATE_CAP:
                in_lang = text_data[0]["locale"]
                # seems like "und" is an unknown language
                if in_lang != "und" and in_lang != lang_flag:
                    translated_line = await self.translate(line, in_lang, lang_flag)
                    translations_count += 1

            field = TextField(translated_line)
            fields.append(field)

            for word in text_data[current_word:]:
                text = word["description"]
                if line.startswith(text):
                    current_word += 1
                    line = line[len(text):].lstrip()
                    field.merge(word["boundingPoly"]["vertices"])
                else:
                    break

        result = await self.bot.loop.run_in_executor(
            None, self.blocking, src, fields
        )

        await ctx.send(file=discord.File(result, filename=f'trocr.png'))

    def blocking(self, src, fields):
        draw = ImageDraw.Draw(src)
        font = ImageFont.truetype(FONT_PATH)

        fields = fields[:BLUR_CAP]

        for field in fields:
            cropped = src.crop(field.coords_padded)
            blurred = cropped.filter(ImageFilter.GaussianBlur(10))
            field.inverted_avg_color = ImageOps.invert(
                blurred.resize((1, 1)).convert("L")
            ).getpixel((0, 0))  # ugly!!!

            src.paste(blurred, field.coords_padded)

            # might not be needed, but fly command creates memory leak
            cropped.close()
            blurred.close()

        for field in fields:
            # TODO: figure out how to fit text into boxes with Pillow
            draw.text(
                (
                    field.left - 2,  # - field.stroke_width * 2,
                    field.upper - field.stroke_width * 2 - 2,
                ),
                text=field.text,
                font=font.font_variant(size=field.font_size),
                spacing=0,
                stroke_width=field.stroke_width,
                stroke_fill=field.inverted_avg_color,  # ugly!!!
            )

        result = BytesIO()
        src.save(result, format='PNG')

        src.close()

        return BytesIO(result.getvalue())
