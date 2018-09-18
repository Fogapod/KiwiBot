from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

import random

from discord import Embed, Colour

try:
    import aiogoogletrans as gt
except ImportError:
	raise ImportError(
        'aiogoogletrans python library is required to use module'
        'You can install it at https://github.com/Fogapod/aiogoogletrans'
)

DEFAULT_CHAIN_LEN = 5
MAX_CHAIN_LEN = 7  # 10 for patrons?

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Translate text'
    long_doc = (
        'Subcommands:\n'
        '\tlist: get list of languages\n\n'
        'Command flags:\n'
        '\t[--out|-o] <language>: output language\n'
        '\t[--len|-l] <number>:   set custom chain len'
    )

    name = 'badtranslator'
    aliases = (name, 'bt')
    category = 'Actions'
    min_args = 1
    bot_perms = (PermissionEmbedLinks(), )
    flags = {
        'out': {
            'alias': 'o',
            'bool': False
        },
        'len': {
            'alias': 'l',
            'bool': False
        }
    }

    async def on_load(self, from_reload):
        self.translator = gt.Translator()

    async def on_call(self, ctx, args, **flags):
        if args[1:].lower() == 'list':
            return '\n'.join(f'`{k}`: {v}' for k, v in gt.LANGUAGES.items())

        out_lang = flags.get('out', 'en').lower()
        if out_lang not in gt.LANGUAGES:
            return '{warning} Invalid out language. Try using list subcommand'

        chain_len = flags.get('len', DEFAULT_CHAIN_LEN)
        if isinstance(chain_len, str) and not chain_len.isdigit():
            return '{error} Wrong value given for chain len'

        chain_len = int(chain_len)
        if chain_len > MAX_CHAIN_LEN:
            return '{warning} Max chain len is %d, you asked for %d' % (MAX_CHAIN_LEN, chain_len)

        if chain_len < 2:
            return '{error} Chain len should not be shorter than 2. Use goodtranslator instead'

        async with ctx.channel.typing():
            langs = random.sample(gt.LANGUAGES.keys(), chain_len + 1)
            if 'en' in langs:
                langs.remove('en')
            langs = langs[:chain_len]
            langs.append(out_lang)

            text = args[1:]
            try:
                for l in langs:
                    translation = await self.translator.translate(text, dest=l)
                    text = translation.text
            except Exception:
                return '{error} Failed to translate. Please, try again later. If there are emojis in text, try removing them.'

            e = Embed(colour=Colour.gold(), title='BadTranslator')
            e.description = text[:2048]
            e.add_field(
                name='Chain',
                value=' -> '.join(gt.LANGUAGES.get(l, l) for l in langs[:-1])
            )
            e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

            await ctx.send(embed=e)

        async def on_unload(self):
            await self.translator.close()
