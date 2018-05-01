from objects.modulebase import ModuleBase

from utils.funcs import create_subprocess_exec, execute_process

from discord import File, FFmpegPCMAudio, PCMVolumeTransformer

from tempfile import TemporaryFile


LANG_LIST = {
    'af': 'afrikaans' ,
    'an': 'aragonese',
    'bg': 'bulgarian',
    'bs': 'bosnian',
    'ca': 'catalan',
    'cs': 'czech',
    'cy': 'welsh',
    'da': 'danish',
    'de': 'german',
    'el': 'greek',
    'en': 'default',
    'en-gb': 'english',
    'en-sc': 'en-scottish',
    'en-uk-north': 'english-north',
    'en-uk-rp': 'english_rp',
    'en-uk-wmids': 'english_wmids',
    'en-us': 'english-us',
   ' en-wi': 'en-westindies',
    'eo': 'esperanto',
    'es': 'spanish',
    'es-la': 'spanish-latin-am',
    'et': 'estonian',
    'fa': 'persian',
    'fa-pin': 'persian-pinglish',
    'fi': 'finnish',
    'fr-be': 'french-Belgium',
    'fr-fr': 'french',
    'ga': 'irish-gaeilge',
    'grc': 'greek-ancient',
    'hi': 'hindi',
    'hr': 'croatian',
    'hu': 'hungarian',  
    'hy': 'armenian', 
    'hy-west': 'armenian-west',
    'id': 'indonesian',
    'is': 'icelandic',
    'it': 'italian',
    'jbo': 'lojban',
    'ka': 'georgian',
    'kn': 'kannada',
    'ku': 'kurdish',
    'la': 'latin',
    'lfn': 'lingua_franca_nova',
    'lt': 'lithuanian',
    'lv': 'latvian',
    'mk': 'macedonian',
    'ml': 'malayalam',
    'ms': 'malay',
    'ne': 'nepali',
    'nl': 'dutch',
    'no': 'norwegian',
    'pa': 'punjabi',
    'pl': 'polish',
    'pt-br': 'brazil',
    'pt-pt ': 'portugal',
    'ro': 'romanian',
    'ru': 'russian',
    'sk': 'slovak',
    'sq': 'albanian',
    'sr': 'serbian',
    'sv': 'swedish',
    'sw': 'swahili-test',
    'ta': 'tamil',
    'tr': 'turkish',
    'vi':'vietnam',
    'vi-hue': 'vietnam_hue',
    'vi-sgn': 'vietnam_sgn',
    'zh': 'Mandarin',
    'zh-yue': 'cantonese'
 }

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Make me say something'
    additional_doc = (
        'Command flags:\n'
        '\t[--file|-f] - respond with audio file\n'
        '\t[--volume|-v] <value> - set volume in %\n'
        '\t[--language|-l] <language> - select prefered language\n\n'
        'Subcommands:\n'
        '\t{prefix}{aliases} list - show list of voices'
    )

    name = 'tts'
    aliases = (name, )
    required_args = 1
    call_flags = {
        'language': {
            'alias': 'l',
            'bool': False
        },
        'file': {
            'alias': 'f',
            'bool': True
        },
         'volume': {
            'alias': 'v',
            'bool': False
        }
    }
    guild_only = True

    async def on_call(self, msg, args, **flags):
        if args[1:].lower() == 'list':
            return '\n'.join(f'`{k}`: {v}' for k, v in LANG_LIST.items())

        if not msg.author.voice:
            return '{warning} Please, join voice channel first'

        try:
            volume = float(flags.get('volume', 100)) / 100
        except ValueError:
            return '{error} Invalid volume value'

        if msg.guild.voice_client is None: 
            vc = await msg.author.voice.channel.connect()
        else:
            vc = msg.guild.voice_client

        if vc.is_playing():
            vc.stop()

        program = ['espeak', args[1:], '--stdout']

        language_flag = flags.get('language')
        if language_flag:
            if language_flag not in LANG_LIST:
                return '{warning} Language not found. Use `list` subcommand to get list of voices'

            program.extend(('-v', LANG_LIST[language_flag]))

        process, pid = await create_subprocess_exec(*program)
        stdout, stderr = await execute_process(process, program)

        with TemporaryFile() as tmp:
            tmp.write(stdout)
            tmp.seek(0)
            audio = PCMVolumeTransformer(FFmpegPCMAudio(tmp, pipe=True), volume)

            if flags.get('file', False):
                await self.send(msg, file=File(stdout, filename='tts.wav'))

        vc.play(audio)