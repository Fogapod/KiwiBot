from objects.modulebase import ModuleBase
from utils.formatters import cleanup_code


API_URL = 'https://run.iomirea.ml/api/v0/languages'

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <language> <program>'
    short_doc = 'Execute code using IOMirea run service'
    long_doc = (
        'Subcommands:\n'
        '\tlist: show list of languages'
    )

    name = 'run'
    aliases = (name, )
    category = 'Services'
    min_args = 1

    async def on_load(self, _):
        self.langs = {}

        async with self.bot.sess.get(API_URL) as r:
            if r.status != 200:
                return
            
            data = await r.json()

        for lang in data:
            for alias in lang["aliases"]:
                self.langs[alias] = lang["name"]

    async def on_call(self, ctx, args, **options):
        result = ''

        if args[1].lower() == 'list':
            last_name = ""
            for k, v in sorted(self.langs.items(), key=lambda x: x[1]):
                if v == last_name:
                    result += ', ' + k
                else:
                    result += f'\n`{v}`: {k}'
                    last_name = v

            return result

        cleaned, from_codeblock = cleanup_code(args[1:])
        if from_codeblock is None:
            lower_input = args[1].lower()

            cleaned, _ = cleanup_code(args[2:])
            # we don't care about parsed language because
            # it's already defined explicitly
        else:
            lower_input = from_codeblock.lower()

        if lower_input in self.langs.values():
            language = lower_input
        else:
            language = self.langs.get(lower_input)

        if not language:
            return await ctx.warn('Invalid language, try checking list of supported languages')

        async with self.bot.sess.post(f"{API_URL}/{language}", json={"code": cleaned}) as r:
            if r.status != 200:
                message = (await r.json())["message"]
                return await ctx.error(f'Error connecting to IOMirea API. Please, try again later: {message}')

            data = await r.json()

        result  = data['stdout']
        result += data['stderr']

        if not result:
            result = 'Empty output'

        return f'```\n{result}```'
