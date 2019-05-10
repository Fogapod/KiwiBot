from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks
from objects.paginators import Paginator

from io import BytesIO
from tempfile import TemporaryFile
from functools import partial

from discord import Embed, Colour, DMChannel, File, FFmpegPCMAudio, PCMVolumeTransformer

import gtts

from utils.voice import connect, play, VoiceConnectionError


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
        '\t[--volume|-v] <value>:      set volume in % from 0 to 200\n'
        '\t[--slow|-s]:                use slow mode if added\n'
        '\t[--language|-l] <language>: select prefered language\n\n'
        'Subcommands:\n'
        '\t{prefix}{aliases} list:     show list of languages'
    )

    name = 'gtts'
    aliases = (name, 'gspeak')
    category = 'Actions'
    min_args = 1
    bot_perms = (PermissionEmbedLinks(), )
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
    ratelimit = (1, 5)

    async def on_load(self, from_reload):
        self.langs = gtts.lang.tts_langs()

    async def on_call(self, ctx, args, **flags):
        if args[1:].lower() == 'list':
            if not hasattr(self, 'langs'):
                return await ctx.error('No languages, probably failed to fetch list')
            lines = [f'{k:<10}| {v}' for k, v in self.langs.items()]
            lines_per_chunk = 30
            chunks = [f'```{"code":<10}| name\n{"-" * 35}\n' + '\n'.join(lines[i:i + lines_per_chunk]) + '```' for i in range(0, len(lines), lines_per_chunk)]

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

        voice_flag = not flags.get(
            'no-voice', isinstance(ctx.channel, DMChannel))

        if voice_flag:
            try:
                vc = await connect(ctx)
            except VoiceConnectionError as e:
                return await ctx.error(e)

        try:
            volume = float(flags.get('volume', 100)) / 100
        except ValueError:
            return await ctx.error('Invalid **volume** value')

        language_flag = flags.get('language')
        if language_flag:
            if language_flag not in self.langs:
                return await ctx.warn('Language not found. Use `list` subcommand to get list of voices')


        tts = gtts.gTTS(
            args[1:], lang=language_flag or 'en',
            slow=flags.get('slow', False), lang_check=False
        )

        with TemporaryFile() as tts_file:
            partial_tts = partial(tts.write_to_fp, tts_file)

            try:
                await self.bot.loop.run_in_executor(None, partial_tts)
            except Exception:
                return await ctx.error('Problem with api response. Please, try again later')

            tts_file.seek(0)

            audio = PCMVolumeTransformer(FFmpegPCMAudio(tts_file, **ffmpeg_options), volume)

            if voice_flag:
                play(vc, audio)
                await ctx.react('✅')

            if flags.get('file', not voice_flag):
                try:
                    tts_file.seek(0)
                    await ctx.send(file=File(BytesIO(tts_file.read()), filename='tts.mp3'))
                except Exception:
                    await ctx.warn('Failed to send file')
