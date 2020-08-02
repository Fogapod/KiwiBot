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

import math
import json
import textwrap
import discord

from io import BytesIO
from collections import deque
from functools import lru_cache

from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageOps

from utils.funcs import find_image


OCR_API_URL = 'https://api.tsu.sh/google/ocr'
TRANSLATE_API_URL = 'https://translate.yandex.net/api/v1.5/tr.json/'

# I have no idea why I have this font in my system, was 1st one I've found
# Docker image should have it
FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

PX_TO_PT_RATIO = 1.3333333

TRANSLATE_CAP = 10
BLUR_CAP = 40


class TROCRException(Exception):
    pass


class AngleUndetectable(TROCRException):
    pass


class TextField:
    def __init__(self, full_text, src, padding=3):
        self.text = full_text

        self.left = None
        self.upper = None
        self.right = None
        self.lower = None

        self.angle = 0

        self._src_width, self._src_height = src.size

        self._padding = padding

    def add_word(self, vertices, src_size):
        if not self.initialized:
            # Get angle from first word
            self.angle = self._get_angle(vertices)

        left, upper, right, lower = self._vertices_to_coords(
            vertices, src_size, self.angle
        )

        self.left = left if self.left is None else min((self.left, left))
        self.upper = upper if self.upper is None else min((self.upper, upper))
        self.right = right if self.right is None else max((self.right, right))
        self.lower = lower if self.lower is None else max((self.lower, lower))

    @staticmethod
    def _vertices_to_coords(vertices, src_size, angle):
        """Returns Pillow style coordinates (left, upper, right, lower)."""

        # A - 0
        # B - 1
        # C - 2
        # D - 3
        #
        # A----B
        # |    |  angle = 360/0
        # D----C
        #
        #    A
        #  /   \
        # D     B  angle = 315
        #  \   /
        #    C
        #
        # D----A
        # |    |  angle = 270
        # C----B
        #
        #    D
        #  /   \
        # C     A  angle = 225
        #  \   /
        #    B
        #
        # C---D
        # |   | angle = 180
        # B---A
        #
        #    C
        #  /   \
        # B     D angle = 135
        #  \   /
        #    A
        #
        # B---C
        # |   | angle = 90
        # A---D
        #
        #    B
        #  /   \
        # A     C  angle = 45
        #  \   /
        #    D
        if 0 <= angle <= 90:
            left  = vertices[0].get("x")
            upper = vertices[1].get("y")
            right = vertices[2].get("x")
            lower = vertices[3].get("y")
        elif 90 < angle <= 180:
            left  = vertices[1].get("x")
            upper = vertices[2].get("y")
            right = vertices[3].get("x")
            lower = vertices[0].get("y")
        elif 180 < angle <= 270:
            left  = vertices[2].get("x")
            upper = vertices[3].get("y")
            right = vertices[0].get("x")
            lower = vertices[1].get("y")
        elif 270 < angle <= 360:
            left  = vertices[3].get("x")
            upper = vertices[0].get("y")
            right = vertices[1].get("x")
            lower = vertices[2].get("y")

        if left is None:
            left = 0
        if upper is None:
            upper = 0
        if right is None:
            right = src_size[0]
        if lower is None:
            lower = src_size[1]

        return (left, upper, right, lower)

    @staticmethod
    def _get_angle(vertices):
        # https://stackoverflow.com/a/27481611
        def get_coords(vertex):
            return vertex.get("x"), vertex.get("y")

        rotatable = deque(vertices)
        for i in range(4):
            x, y = get_coords(rotatable[0])
            next_x, next_y = get_coords(rotatable[1])

            # Any vertex coordinate can be missing
            if None not in (x, y, next_x, next_y):
                x_diff, y_diff = next_x - x, y - next_y
                degrees = math.degrees(math.atan2(y_diff, x_diff))

                # compensate missing vertices
                degrees += 90 * i

                break

            rotatable.rotate(1)
        else:
            raise AngleUndetectable

        if degrees < 0:
            degrees += 360
        elif degrees > 360:
            degreees -= 360

        return degrees

    @property
    def coords(self):
        return (self.left, self.upper, self.right, self.lower)

    @property
    def coords_padded(self):
        return (
            max((0, self.left - self._padding)),
            max((0, self.upper - self._padding)),
            min((self._src_width, self.right + self._padding)),
            min((self._src_height, self.lower + self._padding)),
        )

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.lower - self.upper

    @property
    def font_size(self):
        return max((1, int(PX_TO_PT_RATIO * self.height) - 2))

    @property
    def stroke_width(self):
        return max((1, round(self.font_size / 12)))

    @property
    def initialized(self):
        return None not in self.coords

    def __repr__(self):
        return f"<TextField text='{self.text}' coords={self.coords} angle={self.angle}>"



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
        self.font = ImageFont.truetype(FONT_PATH)

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

    @lru_cache(maxsize=1024)
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

        text_annotations = json["responses"][0].get("textAnnotations")
        if not text_annotations:
            return await ctx.warn("No text detected")

        # Used for error reporting
        notes = ""

        # Google OCR API returns entry for each word separately, but they can be joined
        # by checking full image description. In description words are combined into
        # lines, lines are separated by newlines, there is a trailing newline.
        # Coordinates from words in the same line can be merged
        current_word = 1  # 1st annotation is entire text
        translations_count = 0
        fields = []
        for line in text_annotations[0]["description"].split("\n")[:-1]:
            translated_line = line
            if translations_count < TRANSLATE_CAP:
                in_lang = text_annotations[0]["locale"]
                # seems like "und" is an unknown language
                if in_lang != "und" and in_lang != lang_flag:
                    translated_line = await self.translate(line, in_lang, lang_flag)
                    translations_count += 1

            field = TextField(translated_line, src)

            for word in text_annotations[current_word:]:
                text = word["description"]
                if line.startswith(text):
                    current_word += 1
                    line = line[len(text):].lstrip()
                    # TODO: merge multiple lines into box
                    try:
                        field.add_word(word["boundingPoly"]["vertices"], src.size)
                    except AngleUndetectable:
                        notes += f"angle for `{word}` is undetectable\n"
                else:
                    break

            if field.initialized:
                fields.append(field)

        result = await self.bot.loop.run_in_executor(
            None, self.draw, src, fields
        )

        send_fn = ctx.warn if notes else ctx.send

        await send_fn(notes, file=discord.File(result, filename=f'trocr.png'))

    def draw(self, src, fields):
        src = src.convert("RGBA")

        fields = fields[:BLUR_CAP]

        for field in fields:
            cropped = src.crop(field.coords_padded)

            # NOTE: next line causes segfaults if coords are wrong, debug from here
            blurred = cropped.filter(ImageFilter.GaussianBlur(10))

            # Does not work anymore for some reason, black stroke is good anyway
            # field.inverted_avg_color = ImageOps.invert(
            #     blurred.resize((1, 1)).convert("L")
            # ).getpixel((0, 0))  # ugly!!!

            src.paste(blurred, field.coords_padded)

            # might not be needed, but fly command creates memory leak
            cropped.close()
            blurred.close()

        for field in fields:
            # TODO: figure out how to fit text into boxes with Pillow without creating
            # extra images
            font = self.font.font_variant(size=field.font_size)

            text_im = Image.new(
                "RGBA",
                size=font.getsize(field.text, stroke_width=field.stroke_width),
            )
            draw = ImageDraw.Draw(text_im)

            draw.text(
                (0, 0),
                text=field.text,
                font=font,
                spacing=0,
                stroke_width=field.stroke_width,
                stroke_fill=(0, 0, 0),
            )

            src.alpha_composite(
                text_im.resize(
                    (
                        min((text_im.width, field.width)),
                        min((text_im.height, field.height)),
                    )
                ).rotate(field.angle, expand=True, resample=Image.BICUBIC),
                field.coords_padded[:2],
            )

            text_im.close()

        result = BytesIO()
        src.save(result, format='PNG')

        src.close()

        return BytesIO(result.getvalue())
