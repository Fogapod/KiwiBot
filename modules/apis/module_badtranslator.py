from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

import random

from discord import Embed, Colour


try:
    import aiogoogletrans as gt
except ImportError:
	raise ImportError('aiogoogletrans python library is required to use module')


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Translate text'
    long_doc = (
        'Subcommands:\n'
        '\tlist: get list of languages\n\n'
        'Command flags:\n'
        '\t[--out|-o] <language>: target language'
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
        }
    }

    async def on_load(self, from_reload):
        self.translator = gt.Translator()

        # fix broken languages in aiogoogletrans 3.0
        if 'zh-CN' in gt.LANGUAGES:
            gt.LANGUAGES['zh-cn'] = gt.LANGUAGES['zh-CN']
            del gt.LANGUAGES['zh-CN']

        if 'zh-TW' in gt.LANGUAGES:
            gt.LANGUAGES['zh-tw'] = gt.LANGUAGES['zh-TW']
            del gt.LANGUAGES['zh-TW']

    async def on_call(self, ctx, args, **flags):
        if args[1:].lower() == 'list':
            return '\n'.join(f'`{k}`: {v}' for k, v in gt.LANGUAGES.items())

        out_lang = flags.get('out', 'en').lower()
        if out_lang not in gt.LANGUAGES:
            return '{warning} Invalid out language. Try using list subcommand'

        async with ctx.channel.typing():
            langs = random.sample(gt.LANGUAGES.keys(), 6)
            if 'en' in langs:
                langs.remove('en')
            langs = langs[:5]
            langs.append(out_lang)

            text = args[1:]
            try:
                for l in langs:
                    translation = await self.translator.translate(text, dest=l)
                    text = translation.text
            except Exception:
                return '{error} Failed to translate. Please, try again later'

            e = Embed(colour=Colour.gold(), title='BadTranslator')
            e.description = text[:2048]
            e.add_field(
                name='Chain',
                value=' -> '.join(gt.LANGUAGES[l].title() for l in langs[:-1])
            )
            e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

            await ctx.send(embed=e)