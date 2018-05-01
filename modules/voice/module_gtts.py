from objects.modulebase import ModuleBase

from utils.funcs import create_subprocess_exec, execute_process

from discord import File, FFmpegPCMAudio, PCMVolumeTransformer

import os
import time


TEMP_FILE = 'temp/tts/{}.mp3'


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Make me say something (Google engine)'
    additional_doc = (
        'Command flags:\n'
        '\t[--slow|-s] - use slow mode\n'
        '\t[--file|-f] - respond with audio file\n'
        '\t[--volume|-v] <value> - set volume in %'
    )


    name = 'gtts'
    aliases = (name, )
    required_args = 1
    call_flags = {
        'slow': {
            'alias': 's',
            'bool': True
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
        program = ['gtts-cli', args[1:], '-o', temp_file]

        if flags.get('slow', False):
            program.append('--slow')

        process, pid = await create_subprocess_exec(*program)
        stdout, stderr = await execute_process(process, program)

        audio = PCMVolumeTransformer(FFmpegPCMAudio(temp_file), volume)
        print(dir(audio))

        if flags.get('file', False):
            await self.send(msg, file=File(temp_file))

        vc.play(audio, after=lambda e: os.remove(temp_file))