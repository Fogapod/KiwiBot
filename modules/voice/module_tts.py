from objects.modulebase import ModuleBase

import random

from tempfile import TemporaryFile

from discord import DMChannel, File, FFmpegPCMAudio, PCMVolumeTransformer

from utils.funcs import create_subprocess_exec, execute_process


ffmpeg_options = {
    'pipe': True,
    'options': '-v 0'
}

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
    'en': 'english',
    'en-sc': 'en-scottish',
    'en-uk-north': 'english-north',
    'en-uk-rp': 'english_rp',
    'en-uk-wmids': 'english_wmids',
    'en-us': 'english-us',
    'en-wi': 'en-westindies',
    'eo': 'esperanto',
    'es': 'spanish',
    'es-la': 'spanish-latin-am',
    'et': 'estonian',
    'fa': 'persian',
    'fa-pin': 'persian-pinglish',
    'fi': 'finnish',
    'fr': 'french',
    'fr-be': 'french-Belgium',
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
    'pt': 'portugal',
    'pt-br': 'brazil',
    'ro': 'romanian',
    'ru': 'russian',
    'sk': 'slovak',
    'sq': 'albanian',
    'sr': 'serbian',
    'sv': 'swedish',
    'sw': 'swahili-test',
    'ta': 'tamil',
    'tr': 'turkish',
    'vi': 'vietnam',
    'vi-hue': 'vietnam_hue',
    'vi-sgn': 'vietnam_sgn',
    'zh': 'Mandarin',
    'zh-yue': 'cantonese'
}

ADDITIONAL_LANGS = {
    'en1': 'mb-en1',
    'de2': 'mb-de2'
}

LANG_LIST.update(ADDITIONAL_LANGS)

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Make me say something'
    long_doc = (
        'Command flags:\n'
        '\t[--file|-f]:                respond with audio file\n'
        '\t[--no-voice|-n]:            don\'t use voice channel\n'
        '\t[--volume|-v] <value>:      set volume in %\n'
        '\t[--speed|-s] <value>:       set speed value (default is 175)\n'
        '\t[--language|-l] <language>: select prefered language\n'
        '\t[--woman|-w]:               use female voice if added\n'
        '\t[--quiet|-q]:               whisper text if added\n\n'
        'Subcommands:\n'
        '\t{prefix}{aliases} list:     show list of voices'
    )

    name = 'tts'
    aliases = (name, 'speak')
    category = 'Actions'
    min_args = 1
    flags = {
        'language': {
            'alias': 'l',
            'bool': False
        },
        'file': {
            'alias': 'f',
            'bool': True
        },
        'no-voice': {
            'alias': 'n',
            'bool': True
        },
        'volume': {
            'alias': 'v',
            'bool': False
        },
        'speed': {
            'alias': 's',
            'bool': False
        },
        'woman': {
            'alias': 'w',
            'bool': True
        },
        'quiet': {
            'alias': 'q',
            'bool': True
        }
    }

    async def on_call(self, ctx, args, **flags):
        if args[1:].lower() == 'list':
            return '\n'.join(f'`{k}`: {v}' for k, v in LANG_LIST.items())

        text = args[1:]

        voice_flag = not flags.get(
            'no-voice', isinstance(ctx.channel, DMChannel))

        if voice_flag:
            if not ctx.author.voice:
                return '{warning} Please, join voice channel first'

            if not ctx.author.voice.channel.permissions_for(ctx.author).speak:
                return '{error} You\'re muted!'

            if not ctx.author.voice.channel.permissions_for(ctx.guild.me).connect:
                return '{error} I don\'t have permission to connect to the voice channel'

            if ctx.guild.voice_client is None:
                try:
                    vc = await ctx.author.voice.channel.connect()
                except Exception:
                    return '{warning} Failed to connect to voice channel'
            else:
                vc = ctx.guild.voice_client

        try:
            volume = float(flags.get('volume', 100)) / 100
        except ValueError:
            return '{error} Invalid volume value'

        program = ['espeak', text, '--stdout']

        speed_flag = flags.get('speed')
        if speed_flag is not None:
            try:
                speed = int(speed_flag)
            except ValueError:
                return '{error} Invalid speed value'

            program.extend(('-s', str(speed)))

        language_flag = flags.get('language', 'en')

        if language_flag not in LANG_LIST:
            return '{warning} Language not found. Use `list` subcommand to get list of voices'

        language = LANG_LIST[language_flag]

        woman_flag = flags.get('woman', False)
        quiet_flag = flags.get('quiet', False)

        if woman_flag:
            if quiet_flag:
                return '{error} Can\'t apply both woman and quiet flags'

            language += f'+f{random.randrange(1, 5)}'

        elif quiet_flag:
            language += '+whisper'
        else:
            language += f'+m{random.randrange(1, 8)}'

        program.extend(('-v', language))

        process, pid = await create_subprocess_exec(*program)
        stdout, stderr = await execute_process(process)

        with TemporaryFile() as tmp:
            tmp.write(stdout)
            tmp.seek(0)
            audio = PCMVolumeTransformer(FFmpegPCMAudio(tmp, **ffmpeg_options), volume)

            if flags.get('file', not voice_flag):
                try:
                    await ctx.send(file=File(stdout, filename='tts.wav'))
                except Exception:
                    await ctx.send('Failed to send file')

        if voice_flag:
            if vc.is_playing():
                vc.stop()

            vc.play(audio)
            await ctx.react('✅')