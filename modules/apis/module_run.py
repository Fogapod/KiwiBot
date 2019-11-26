from objects.modulebase import ModuleBase
from utils.formatters import cleanup_code


API_URL = 'https://run.iomirea.ml/api/v0/languages'

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <language> [program]'
    short_doc = 'Execute code using IOMirea run service'
    long_doc = (
        'Subcommands:\n'
        '\tlist: show list of languages\n'
        '\texample <language>: shows example program\n\n'
        'Available flags:\n'
        '\t [-i|--input] <text>: send text to stdin'
    )

    name = 'run'
    aliases = (name, )
    category = 'Services'
    flags = {
        'input': {
            'alias': 'i',
            'bool': False
        }
    }

    min_args = 1

    async def on_load(self, _):
        self.langs = {}

        async with self.bot.sess.get(API_URL) as r:
            if r.status != 200:
                return
            
            data = await r.json()

        for lang in data:
            for alias in lang["aliases"]:
                self.langs[alias] = lang

    def _get_language(self, alias):
        alias = alias.lower()

        # inefficient
        for l in self.langs.values():
            if alias == l["name"]:
                return l

        return self.langs.get(alias)

    async def on_call(self, ctx, args, **options):
        async with ctx.channel.typing():
            return await self._on_call(ctx, args, **options)

    async def _on_call(self, ctx, args, **options):
        result = ''

        if args[1].lower() == 'list':
            last_name = ""
            for k, v in sorted(self.langs.items(), key=lambda x: x[1]["name"]):
                if v == last_name:
                    result += ', ' + k
                else:
                    result += f'\n`{v["name"]}`: {k}'
                    last_name = v

            return result

        if args[1].lower() == 'example':
            if len(args) < 3:
                return await ctx.warn('No language argument provided')

            language = self._get_language(args[2])
            if not language:
                return await ctx.warn(
                    'Unknown language, try checking list of supported languages'
                )

            nl = '\n'
            return f'```{language["name"]}{nl}{language["example"]}```'

        cleaned, from_codeblock = cleanup_code(args[1:])
        if from_codeblock is None:
            input_lang = args[1]

            cleaned, _ = cleanup_code(args[2:])
            # we don't care about parsed language because
            # it's already defined explicitly
        else:
            input_lang = from_codeblock

        language = self._get_language(input_lang)

        if not language:
            return await ctx.warn(
                'Invalid language, try checking list of supported languages'
            )

        payload = {}
        if cleaned:
            payload['code'] = cleaned

        inp = options.get('input')
        if inp is not None:
            payload['input'] = inp.encode("raw_unicode_escape").decode('unicode_escape')

        async with self.bot.sess.post(
                f'{API_URL}/{language["name"]}', params=dict(merge='1'),
                json=payload
        ) as r:
            if r.status != 200:
                message = (await r.json())['message']
                return await ctx.error(
                    f'Error connecting to IOMirea API. Please, try again later: {message}'
                )

            data = await r.json()

        return f'```\n{data["stdout"]}\n\nexit code: {data["exit_code"]} | ran for: {round(data["exec_time"], 3)}s```'
