from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks
from objects.paginators import Paginator

import random

from tempfile import TemporaryFile

from discord import Embed, Colour, DMChannel, File, FFmpegPCMAudio, PCMVolumeTransformer

from utils.funcs import create_subprocess_exec, execute_process


ffmpeg_options = {
    'pipe': True,
    'options': '-v 0'
}

LANG_LIST = {
    'af': 'Afrikaans',
    'am': 'Amharic',
    'an': 'Aragonese',
    'ar': 'Arabic',
    'as': 'Assamese',
    'az': 'Azerbaijani',
    'bg': 'Bulgarian',
    'bn': 'Bengali',
    'bpy': 'Bishnupriya_Manipuri',
    'bs': 'Bosnian',
    'ca': 'Catalan',
    'cmn': 'Chinese_(Mandarin)',
    'cs': 'Czech',
    'cy': 'Welsh',
    'da': 'Danish',
    'de': 'German',
    'el': 'Greek',
    'en-029': 'English_(Caribbean)',
    # 'en-gb': 'English_(Great_Britain)',
    'en-gb-scotland': 'English_(Scotland)',
    'en-gb-x-gbclan': 'English_(Lancaster)',
    'en-gb-x-gbcwmd': 'English_(West_Midlands)',
    'en-gb-x-rp': 'English_(Received_Pronunciation)',
    'en-us': 'English_(America)',
    'eo': 'Esperanto',
    'es': 'Spanish_(Spain)',
    'es-419': 'Spanish_(Latin_America)',
    'et': 'Estonian',
    'eu': 'Basque',
    'fa': 'Persian',
    'fa-Latn': 'Persian_(Pinglish)',
    'fi': 'Finnish',
    'fr-be': 'French_(Belgium)',
    'fr-ch': 'French_(Switzerland)',
    'fr-fr': 'French_(France)',
    'ga': 'Gaelic_(Irish)',
    'gd': 'Gaelic_(Scottish)',
    'gn': 'Guarani',
    'grc': 'Greek_(Ancient)',
    'gu': 'Gujarati',
    'hi': 'Hindi',
    'hr': 'Croatian',
    'hu': 'Hungarian',
    'hy': 'Armenian_(East_Armenia)',
    'hy-arevmda': 'Armenian_(West_Armenia)',
    'ia': 'Interlingua',
    'id': 'Indonesian',
    'is': 'Icelandic',
    'it': 'Italian',
    'ja': 'Japanese',
    'jbo': 'Lojban',
    'ka': 'Georgian',
    'kl': 'Greenlandic',
    'kn': 'Kannada',
    'ko': 'Korean',
    'kok': 'Konkani',
    'ku': 'Kurdish',
    'ky': 'Kyrgyz',
    'la': 'Latin',
    'lfn': 'Lingua_Franca_Nova',
    'lt': 'Lithuanian',
    'lv': 'Latvian',
    'mi': 'poz/mi',
    'mk': 'Macedonian',
    'ml': 'Malayalam',
    'mr': 'Marathi',
    'ms': 'Malay',
    'mt': 'Maltese',
    'my': 'Burmese',
    'nb': 'Norwegian_Bokmål',
    'nci': 'Nahuatl_(Classical)',
    'ne': 'Nepali',
    'nl': 'Dutch',
    'om': 'Oromo',
    'or': 'Oriya',
    'pa': 'Punjabi',
    'pap': 'Papiamento',
    'pl': 'Polish',
    'pt': 'Portuguese_(Portugal)',
    'pt-br': 'Portuguese_(Brazil)',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sd': 'Sindhi',
    'si': 'Sinhala',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'sq': 'Albanian',
    'sr': 'Serbian',
    'sv': 'Swedish',
    'sw': 'Swahili',
    'ta': 'Tamil',
    'te': 'Telugu',
    'tn': 'Setswana',
    'tr': 'Turkish',
    'tt': 'Tatar',
    'ur': 'Urdu',
    'vi': 'Vietnamese_(Northern)',
    'vi-vn-x-central': 'Vietnamese_(Central)',
    'vi-vn-x-south': 'Vietnamese_(Southern)',
    'yue': 'Chinese_(Cantonese)'
}

ADDITIONAL_LANGS = {
    'mb-en1': 'Better English 1',
    'mb-us1': 'Better US English 1',
    'mb-de1': 'Better German 1',
    'mb-de2': 'Better German 2'
}

LANG_LIST.update(ADDITIONAL_LANGS)

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Make me say something'
    long_doc = (
        'Command flags:\n'
        '\t[--file|-f]:                respond with audio file\n'
        '\t[--no-voice|-n]:            don\'t use voice channel\n'
        '\t[--volume|-v] <value>:      set volume in % from 0 to 200\n'
        '\t[--speed|-s] <value>:       set speed value from 0 (default is 115)\n'
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
    bot_perms = (PermissionEmbedLinks(), )
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
            lines = [f'{k:<15}| {v}' for k, v in LANG_LIST.items()]
            lines_per_chunk = 30
            chunks = [f'```{"code":<15}| name\n{"-" * 45}\n' + '\n'.join(lines[i:i + lines_per_chunk]) + '```' for i in range(0, len(lines), lines_per_chunk)]

            p = Paginator(self.bot)
            for i, chunk in enumerate(chunks):
                e = Embed(
                    title=f'Supported languages ({len(lines)})',
                    colour=Colour.gold(),
                    description=chunk
                )
                e.set_footer(text=f'Page {i + 1} / {len(chunks)}')
                p.add_page(embed=e)

            return await p.run(ctx)

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

        program = ['espeak-ng', text, '--stdout']

        speed_flag = flags.get('speed')
        if speed_flag is not None:
            try:
                speed = int(speed_flag) + 80
            except ValueError:
                return '{error} Invalid speed value'

            program.extend(('-s', str(speed)))

        language_flag = flags.get('language', 'en-us')

        if language_flag not in LANG_LIST:
            return '{warning} Language not found. Use `list` subcommand to get list of voices'

        language = language_flag

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