from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

from utils.funcs import find_user, find_channel

from discord import DMChannel


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Let me say something for you, lazy human.'
    additional_doc = (
        'Command flags:\n'
        '\t--delete  or -d:           Delete command message if added\n'
        '\t--channel or -c <channel>: Channel where to send message\n'
        '\t--user    or -u <user>:    Target user to send direct message'
    )

    name = 'say'
    aliases = (name, )
    required_args = 1
    call_flags = {
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
        }
    }

    async def on_call(self, msg, args, **flags):
        channel = flags.get('channel', None)
        user = flags.get('user', None)

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

        is_same_place = getattr(channel, 'guild', None) == getattr(msg, 'guild', None)
        if not is_same_place:
            if not PermissionBotOwner().check(msg.channel, msg.author):
                return '{warning} Only bot owner can send messages to other guilds or users'
        elif not channel.permissions_for(msg.author).send_messages:
            return '{warning} You don\'t have permission to send messages to this channel'

        if flags.get('delete', False):
            await self.bot.delete_message(msg)

        m = await self.send(msg, channel=channel, content=args[1:])
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