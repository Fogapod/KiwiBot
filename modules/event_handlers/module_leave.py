from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageGuild

from utils.formatters import lazy_format

from discord import Forbidden, NotFound


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [leave text]'
    short_doc = 'Allows to set message on guild user leave.'
    additional_doc = (
        'Leave message support several keys.\n'
        'Keys are replaced to match user.\n'
        'Currently available keys:\n'
        '\t{mention} - @mentions user\n'
        '\t{name} - user name\n'
        '\t{discrim} - user discriminator\n'
        '\t{guild} - guild name\n'
        '\t{id} - user id'
    )

    name = 'leave'
    aliases = (name, )
    guild_only = True

    async def on_load(self, from_reload):
        if from_reload:
            return

        self.events = {
            'member_remove': self.on_member_leave
        }

    async def on_member_leave(self, member):
        record = await self.bot.redis.get(f'leave_message:{member.guild.id}')
        if record:
            channel, _, leave_message = record.partition(':')
            leave_message = lazy_format(
                leave_message,
                mention=member.mention,
                name=member.name,
                discrim=member.discriminator,
                guild=member.guild.name,
                id=member.id
            )
            try:
                await member.guild.get_channel(int(channel)).send(leave_message)
            except (Forbidden, NotFound):
                pass

    async def on_call(self, msg, args, **flags):
        if len(args) == 1:
            record = await self.bot.redis.get(f'leave_message:{msg.guild.id}')
            if record:
                channel, _, leave_message = record.partition(':')
                return f'Current leave message: {leave_message}\nChannel: **{channel}**'
            else:
                return '{warning} Leave message not set'

        manage_guild_perm = PermissionManageGuild()
        if not manage_guild_perm.check(msg.channel, msg.author):
            raise manage_guild_perm

        if args[1:].lower() in ('delete', 'remove'):
            await self.bot.redis.delete(f'leave_message:{msg.guild.id}')
            return 'Leave message removed'

        await self.bot.redis.set(f'leave_message:{msg.guild.id}', f'{msg.channel.id}:{args[1:]}')
        await self.bot.delete_message(msg)
        await self.send(
            msg, delete_after=7,
            content='Set leave message in this channel.'
        )