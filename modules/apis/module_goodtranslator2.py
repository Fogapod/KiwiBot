from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from discord import Embed, Colour


API_URL = 'https://translate.yandex.net/api/v1.5/tr.json/'

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

    name = 'goodtranslator2'
    aliases = (name, 'gt2')
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
        self.api_key = self.bot.config.get('yandex_api_key')
        if self.api_key:
            params = {
                'key': self.api_key,
                'ui': 'en'
            }

            async with self.bot.sess.get(API_URL + 'getLangs', params=params) as r:
                if r.status == 200:
                    self.langs = (await r.json())['langs']
                    return

        raise Exception('No yandex api key in config or key is invalid')

    async def on_call(self, ctx, args, **flags):
        if args[1:].lower() == 'list':
            return '\n'.join(f'`{k}`: {v}' for k, v in self.langs.items())

        in_lang = flags.get('in', None)
        if in_lang and in_lang.lower() not in self.langs:
            return await ctx.warn('Invalid input language. Try using list subcommand')

        out_lang = flags.get('out', 'en').lower()
        if out_lang not in self.langs:
            return await ctx.warn('Invalid out language. Try using list subcommand')

        params = {
            'key': self.api_key,
            'text': args[1:],
            'lang': out_lang if in_lang is None else f'{in_lang}-{out_lang}'
        }

        try:
            async with self.bot.sess.post(API_URL + 'translate', params=params) as r:
                if r.status != 200:
                    return await ctx.error('Failed to translate. Please, try again later')
                r_json = await r.json()
                text = r_json['text'][0]
                source, destination = r_json['lang'].split('-')
        except Exception:
            return await ctx.error('Failed to translate. Please, try again later')

        e = Embed(colour=Colour.gold(), title='GoodTranslator 2')
        e.description = text[:2048]
        e.add_field(
            name='Translated',
            value=f'{self.langs.get(source, source)} -> {self.langs[destination]}'
        )
        e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=e)
