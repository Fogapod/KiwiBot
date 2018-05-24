from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner, PermissionSendTtsMessages

from utils.funcs import find_user, find_channel, check_permission

from discord import DMChannel


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Let me say something for you, lazy human'
    long_doc = (
        'Command flags:\n'
        '\t[--delete|-d]:            Delete command message if added\n'
        '\t[--channel|-c] <channel>: Channel where to send message\n'
        '\t[--user|-u] <user>:       Target user to send direct message\n'
        '\t[--tts|-t]:               Send message as text-to-speech if added'
    )

    name = 'say'
    aliases = (name, )
    category = 'Actions'
    min_args = 1
    flags = {
        'delete': {
            'alias': 'd',
            'bool': True
        },
        'channel': {
            'alias': 'c',
            'bool': False
        },
        'user': {
            'alias': 'u',
            'bool': False
        },
        'tts': {
            'alias': 't',
            'bool': True
        }
    }

    async def on_call(self, ctx, args, **flags):
        channel = flags.get('channel', None)
        user = flags.get('user', None)
        tts = flags.get('tts', False)

        if channel and user:
            return '{warning} channel and user flags are conflicting'

        if channel:
            channel = await find_channel(
                channel, ctx.guild, global_id_search=True,
                include_voice=False, include_category=False
            )
            if channel is None:
                return '{warning} Channel not found'

        elif user:
            user = await find_user(user, ctx.message)
            if user is None:
                return '{warning} User not found'

            if user.bot:
                return '{warning} Can\'t send message to bot'

            channel = user.dm_channel
            if channel is None:
                channel = await user.create_dm()

        if channel is None:
            channel = ctx.channel

        if tts:
            check_permission(
                PermissionSendTtsMessages(), ctx.channel, self.bot.user)
            check_permission(
                PermissionSendTtsMessages(), ctx.channel, ctx.author)

        is_same_place = getattr(channel, 'guild', None) == ctx.guild
        if not is_same_place:
            if not PermissionBotOwner().check(ctx.channel, ctx.author):
                return '{warning} Only bot owner can send messages to other guilds or users'
        elif not channel.permissions_for(ctx.author).send_messages:
            return '{warning} You don\'t have permission to send messages to this channel'

        delete_message = flags.get('delete', False)
        if delete_message:
            await self.bot.delete_message(ctx.message)

        m = await ctx.send(
            args[1:], channel=channel, tts=tts, register=not delete_message)
        if m is None:
            return '{error} Failed to deliver message. (blocked by user/no common servers/no permission to send messages to this channel)'

        if not is_same_place:
            if isinstance(m.channel, DMChannel):
                destination = m.channel.recipient
            else:
                destination = f'{channel.mention}** on **{m.guild}'
            return f'Sent message to **{destination}**'