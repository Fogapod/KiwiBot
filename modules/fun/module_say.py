from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

from utils.funcs import find_user

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
            if channel.isdigit():
                channel = self.bot.get_channel(int(channel))
            else:
                return '{warning} Invalid channel id given'
            if channel is None:
                return '{warning} Channel not found'
        elif user:
            user = await find_user(user, msg, self.bot)
            if user is None:
                return '{warning} User not found'

            channel = user.dm_channel
            if channel is None:
                channel = await user.create_dm()

        if channel is None:
            channel = msg.channel

        is_same_place = getattr(channel, 'guild', None) == getattr(msg, 'guild', None)
        if not is_same_place:
            if not await PermissionBotOwner().check(msg.channel, msg.author):
                return '{warning} Can\'t send messages to other guilds or users'

        if flags.get('delete', False):
            await self.bot.delete_message(msg)

        try:
            m = await channel.send(args[1:])
        except Exception as e:
            return '{error} Failed to deliver message: **%s**' % e.__class__.__name__
        else:
            if not is_same_place:
                if isinstance(m.channel, DMChannel):
                    destination = m.channel.recipient
                else:
                    destination = f'{channel.mention}** on **{m.guild}'
                return f'Sent message to **{destination}**'