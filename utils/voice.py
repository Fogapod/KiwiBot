class VoiceConnectionError(Exception):
    pass


async def connect(ctx):
    if ctx.guild is None:
        raise VoiceConnectionError('Please, use this in a guild channel')

    if not ctx.author.voice:
        raise VoiceConnectionError('Please, join voice channel first')

    if not ctx.author.voice.channel.permissions_for(ctx.author).speak:
        raise VoiceConnectionError('You are muted!')

    if not ctx.author.voice.channel.permissions_for(ctx.guild.me).connect:
        raise VoiceConnectionError(
            'I do not have permission to connect to voice channel')

    if ctx.guild.voice_client is None:
        try:
            return await ctx.author.voice.channel.connect()
        except Exception as e:
            raise VoiceConnectionError(
                f'Failed to connect to a voice channel: {e}')

    elif ctx.author not in ctx.guild.voice_client.channel.members:
        await ctx.guild.voice_client.move_to(ctx.author.voice.channel)

    return ctx.guild.voice_client

def play(vc, audio):
    if vc.is_playing():
        vc.stop()

    vc.play(audio)
