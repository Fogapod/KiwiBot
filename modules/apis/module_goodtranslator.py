from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from discord import Embed, Colour


try:
    import aiogoogletrans as gt
except ImportError:
	raise ImportError(
        'aiogoogletrans python library is required to use module'
        'You can install it at https://github.com/Fogapod/aiogoogletrans'
    )


translate_urls = [
    'translate.google.com', 'translate.google.co.kr',
    'translate.google.at', 'translate.google.de',
    'translate.google.ru', 'translate.google.ch',
    'translate.google.fr', 'translate.google.es'
]

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Translate text'
    long_doc = (
        'Subcommands:\n'
        '\tlist: get list of languages\n\n'
        'Command flags:\n'
        '\t[--in|-i] <language>:  input language\n'
        '\t[--out|-o] <language>: output language'
    )

    name = 'goodtranslator'
    aliases = (name, 'gt')
    category = 'Actions'
    min_args = 1
    bot_perms = (PermissionEmbedLinks(), )
    flags = {
        'in': {
            'alias': 'i',
            'bool': False
        },
        'out': {
            'alias': 'o',
            'bool': False
        }
    }

    async def on_load(self, from_reload):
        self.translator = gt.Translator(
            service_urls=translate_urls, proxies=list(self.bot.proxies.keys()) + [None])

    async def on_call(self, ctx, args, **flags):
        if args[1:].lower() == 'list':
            return '\n'.join(f'`{k}`: {v}' for k, v in gt.LANGUAGES.items())

        in_lang = flags.get('in', None)
        if in_lang and in_lang.lower() not in gt.LANGUAGES:
            return await ctx.warn('Invalid input language. Try using list subcommand')

        out_lang = flags.get('out', 'en').lower()
        if out_lang not in gt.LANGUAGES:
            return await ctx.warn('Invalid out language. Try using list subcommand')

        try:
            translation = await self.translator.translate(
                args[1:], src=in_lang or 'auto', dest=out_lang)
        except Exception:
            return await ctx.error(
                'Failed to translate. Please, try again later. '
                'If there are emojis in text, try removing them'
            )

        e = Embed(colour=Colour.gold(), title='GoodTranslator')
        e.description = translation.text[:2048]
        e.add_field(
            name='Translated',
            value=f'{gt.LANGUAGES.get(translation.src, translation.src)} -> {gt.LANGUAGES[out_lang]}'
        )
        e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=e)

    async def on_unload(self):
        await self.translator.close()
