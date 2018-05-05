from objects.modulebase import ModuleBase

from utils.funcs import create_subprocess_exec, execute_process

from discord import DMChannel, File, FFmpegPCMAudio, PCMVolumeTransformer

from tempfile import TemporaryFile

from gtts.lang import tts_langs


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Make me say something (Google engine).'
    additional_doc = (
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
    aliases = (name, )
    required_args = 1
    call_flags = {
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
        self.langs = tts_langs()

    async def on_call(self, msg, args, **flags):
        if args[1:].lower() == 'list':
            return '\n'.join(f'`{k}`: {v}' for k, v in self.langs.items())

        text = args[1:]
        if len(text) > 1000:
            return '{warning} Text is too long (> 1000 characters)'

        voice_flag = not flags.get(
            'no-voice', isinstance(msg.channel, DMChannel))

        if voice_flag and not msg.author.voice:
            return '{warning} Please, join voice channel first'

        try:
            volume = float(flags.get('volume', 100)) / 100
        except ValueError:
            return '{error} Invalid volume value'

        program = ['gtts-cli', text]

        language_flag = flags.get('language')
        if language_flag:
            if language_flag not in self.langs:
                return '{warning} language not found. Use `list` subcommand to get list of voices'

            program.extend(('-l', language_flag))

        if flags.get('slow', False):
            program.append('--slow')

        process, pid = await create_subprocess_exec(*program)
        stdout, stderr = await execute_process(process, program)

        with TemporaryFile() as tmp:
            tmp.write(stdout)
            tmp.seek(0)
            audio = PCMVolumeTransformer(FFmpegPCMAudio(tmp, pipe=True), volume)

            if flags.get('file', not voice_flag):
                await self.send(msg, file=File(stdout, filename='tts.mp3'))

        if voice_flag:
            if msg.guild.voice_client is None:
                vc = await msg.author.voice.channel.connect()
            else:
                vc = msg.guild.voice_client

            if vc.is_playing():
                vc.stop()

            vc.play(audio)