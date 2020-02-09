from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks, PermissionAttachFiles

from io import BytesIO

from discord import Embed, Colour, File

from constants import ID_REGEX, EMOJI_REGEX


EMOJI_ENDPOINT = 'https://cdn.discordapp.com/emojis/{}'
TWEMOJI_ENDPOINT = 'https://bot.mods.nyc/twemoji/{}.png'


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <emoji>'
    short_doc = 'Allows to get emoji image'

    name = 'emoji'
    aliases = (name, 'e')
    category = 'Discord'
    min_args = 1
    max_args = 1
    bot_perms = (PermissionEmbedLinks(), PermissionAttachFiles())

    async def on_call(self, ctx, args, **flags):
        e = Embed(colour=Colour.gold())
        f = None

        text = args[1:]
        emoji_id = None
        emoji_name = ''

        id_match = ID_REGEX.fullmatch(text)

        if id_match:
            emoji_id = int(id_match.group(0))
        else:
            emoji_match = EMOJI_REGEX.fullmatch(text)
            if emoji_match:
                groups = emoji_match.groupdict()
                emoji_id = int(groups['id'])
                emoji_name = groups['name']

        if emoji_id is None:
            # thanks discord for this nonsense
            text = text.rstrip("\N{VARIATION SELECTOR-16}")

            code = '-'.join(map(lambda c: f'{ord(c):x}', text))
            async with self.bot.sess.get(TWEMOJI_ENDPOINT.format(code)) as r:
                if r.status != 200:
                    return await ctx.warn('Could not get emoji from input text')
                        
                filename = 'emoji.png'
                f = File(BytesIO(await r.read()), filename=filename)
                e.title = f'TWEmoji'
                e.set_image(url=f'attachment://{filename}')
        else:
            e.set_footer(text=emoji_id)
            emoji = self.bot.get_emoji(emoji_id)
            if emoji is None:
                async with self.bot.sess.get(EMOJI_ENDPOINT.format(emoji_id)) as r:
                    if r.status != 200:
                        return await ctx.error('Emoji with given id not found')
                        
                    filename = f'emoji.{r.content_type[6:]}'
                    f = File(BytesIO(await r.read()), filename=filename)
                    e.title = f'Emoji {emoji_name or ""}'
                    e.set_image(url=f'attachment://{filename}')
            else:
                e.title = f'Emoji {emoji.name}'
                e.set_image(url=emoji.url)

        await ctx.send(embed=e, file=f)
