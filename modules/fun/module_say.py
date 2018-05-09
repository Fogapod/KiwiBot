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

    async def on_call(self, msg, args, **flags):
        channel = flags.get('channel', None)
        user = flags.get('user', None)
        tts = flags.get('tts', False)

        if channel and user:
            return '{warning} channel and user flags are conflicting'

        if channel:
            channel = await find_channel(
                channel, msg.guild, self.bot, global_id_search=True,
                include_voice=False, include_category=False
            )
            if channel is None:
                return '{warning} Channel not found'

        elif user:
            user = await find_user(user, msg, self.bot)
            if user is None:
                return '{warning} User not found'

            if user.bot:
                return '{warning} Can\'t send message to bot'

            channel = user.dm_channel
            if channel is None:
                channel = await user.create_dm()

        if channel is None:
            channel = msg.channel

        if tts:
            check_permission(
                PermissionSendTtsMessages(), msg.channel, self.bot.user)
            check_permission(
                PermissionSendTtsMessages(), msg.channel, msg.author)

        is_same_place = getattr(channel, 'guild', None) == getattr(msg, 'guild', None)
        if not is_same_place:
            if not PermissionBotOwner().check(msg.channel, msg.author):
                return '{warning} Only bot owner can send messages to other guilds or users'
        elif not channel.permissions_for(msg.author).send_messages:
            return '{warning} You don\'t have permission to send messages to this channel'

        if flags.get('delete', False):
            await self.bot.delete_message(msg)

        m = await self.send(msg, channel=channel, content=args[1:], tts=tts)
        if m is None:
            return '{error} Failed to deliver message. (blocked by user/no common servers/no permission to send messages to this channel)'
        else:
            await self.bot.register_response(msg, m)
            if not is_same_place:
                if isinstance(m.channel, DMChannel):
                    destination = m.channel.recipient
                else:
                    destination = f'{channel.mention}** on **{m.guild}'
                return f'Sent message to **{destination}**'