from objects.modulebase import ModuleBase

from tempfile import TemporaryFile
from functools import partial

from discord import DMChannel, File, FFmpegPCMAudio, PCMVolumeTransformer

import gtts


ffmpeg_options = {
    'pipe': True,
    'options': '-v 0'
}

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Make me say something (Google engine)'
    long_doc = (
        'Command flags:\n'
        '\t[--file|-f]:                respond with audio file\n'
        '\t[--no-voice|-n]:            don\'t use voice channel\n'
        '\t[--volume|-v] <value>:      set volume in %\n'
        '\t[--slow|-s]:                use slow mode\n'
        '\t[--language|-l] <language>: select prefered language\n\n'
        'Subcommands:\n'
        '\t{prefix}{aliases} list:     show list of languages'
    )

    name = 'gtts'
    aliases = (name, 'gspeak')
    category = 'Actions'
    min_args = 1
    flags = {
        'language': {
            'alias': 'l',
            'bool': False
        },
        'slow': {
            'alias': 's',
            'bool': True
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
        }
    }

    async def on_load(self, from_reload):
        self.langs = gtts.lang.tts_langs()

    async def on_call(self, ctx, args, **flags):
        if args[1:].lower() == 'list':
            return '\n'.join(f'`{k}`: {v}' for k, v in self.langs.items())

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

        language_flag = flags.get('language')
        if language_flag:
            if language_flag not in self.langs:
                return '{warning} language not found. Use `list` subcommand to get list of voices'


        tts = gtts.gTTS(
            args[1:], lang=language_flag or 'en',
            slow=flags.get('slow', False), lang_check=False
        )

        with TemporaryFile() as tts_file:
            partial_tts = partial(tts.write_to_fp, tts_file)

            try:
                await self.bot.loop.run_in_executor(None, partial_tts)
            except Exception:
                return '{error} Problem with api response. Please, try again later'

            tts_file.seek(0)

            audio = PCMVolumeTransformer(FFmpegPCMAudio(tts_file, **ffmpeg_options), volume)

            if voice_flag:
                if vc.is_playing():
                    vc.stop()

                vc.play(audio)
                await ctx.react('✅')

            if flags.get('file', not voice_flag):
                try:
                    tts_file.seek(0)
                    await ctx.send(file=File(tts_file.read(), filename='tts.mp3'))
                except Exception:
                    await ctx.send('Failed to send file')