from objects.modulebase import ModuleBase

from utils.funcs import create_subprocess_exec, execute_process

from discord import File, FFmpegPCMAudio, PCMVolumeTransformer

import os
import time


TEMP_FILE = 'temp/tts/{}.wav'

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
        '\t[--voice|-o] <voice> - select prefered voice\n\n'
        'Subcommands:\n'
        '\t{prefix}{aliases} list - show list of languages'
    )

    name = 'tts'
    aliases = (name, )
    required_args = 1
    call_flags = {
        'voice': {
            'alias': 'o',
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

        temp_file = TEMP_FILE.format(round(time.time()))
        program = ['espeak', args[1:], '-w', temp_file]

        voice_flag = flags.get('voice')
        if voice_flag:
            if voice_flag not in LANG_LIST:
                return '{warning} Voice not found. Use `list` subcommand to get list of voices'

            program.extend(('-v', LANG_LIST[voice_flag]))

        process, pid = await create_subprocess_exec(*program)
        stdout, stderr = await execute_process(process, program)

        audio = PCMVolumeTransformer(FFmpegPCMAudio(temp_file), volume)

        if flags.get('file', False):
            await self.send(msg, file=File(temp_file))

        vc.play(audio, after=lambda e: os.remove(temp_file))