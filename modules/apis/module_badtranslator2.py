from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

import random

from discord import Embed, Colour


API_URL = 'https://translate.yandex.net/api/v1.5/tr.json/'

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

    name = 'badtranslator2'
    aliases = (name, 'bt2')
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

        out_lang = flags.get('out', 'en').lower()
        if out_lang not in self.langs:
            return '{warning} Invalid out language. Try using list subcommand'

        chain_len = flags.get('len', DEFAULT_CHAIN_LEN)
        if isinstance(chain_len, str) and not chain_len.isdigit():
            return '{error} Wrong value given for chain len'

        chain_len = int(chain_len)
        if chain_len > MAX_CHAIN_LEN:
            return '{warning} Max chain len is %d, you asked for %d' % (MAX_CHAIN_LEN, chain_len)

        if chain_len < 2:
            return '{error} Chain len should not be shorter than 2. Use goodtranslator2 instead'

        async with ctx.channel.typing():
            langs = random.sample(self.langs.keys(), chain_len + 1)
            if 'en' in langs:
                langs.remove('en')
            langs = langs[:chain_len]
            langs.append(out_lang)

            text = args[1:]

            try:
                for i, l in enumerate(langs):
                    params = {
                        'key': self.api_key,
                        'text': text,
                        'lang': f'{langs[i - 1] + "-" if i else ""}{l}'
                    }
                    async with self.bot.sess.post(API_URL + 'translate', params=params) as r:
                        if r.status != 200:
                            return '{error} Failed to translate. Please, try again later'

                        text = (await r.json())['text'][0]
            except Exception:
                return '{error} Failed to translate. Please, try again later'

            e = Embed(colour=Colour.gold(), title='BadTranslator 2')
            e.description = text[:2048]
            e.add_field(
                name='Chain',
                value=' -> '.join(self.langs.get(l, l) for l in langs[:-1])
            )
            e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

            await ctx.send(embed=e)
