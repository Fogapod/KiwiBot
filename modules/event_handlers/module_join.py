from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageGuild

from utils.formatters import lazy_format

from discord import Forbidden, NotFound


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [welcome text]'
    short_doc = 'Allows to set message on guild user join.'
    additional_doc = (
        'Welcome message support several keys.\n'
        'Keys are replaced to match user.\n'
        'Currently available keys:\n'
        '\t{mention} - @mentions user\n'
        '\t{name} - user name\n'
        '\t{discrim} - user discriminator\n'
        '\t{guild} - guild name\n'
        '\t{id} - user id'
    )

    name = 'join'
    aliases = (name, 'welcome')
    guild_only = True

    async def on_load(self, from_reload):
        if from_reload:
            return

        self.events = {
            'member_join': self.on_member_join
        }

    async def on_member_join(self, member):
        record = await self.bot.redis.get(f'join_message:{member.guild.id}')
        if record:
            channel, _, join_message = record.partition(':')
            join_message = lazy_format(
                join_message,
                mention=member.mention,
                name=member.name,
                discrim=member.discriminator,
                guild=member.guild.name,
                id=member.id
            )
            try:
                await member.guild.get_channel(int(channel)).send(join_message)
            except (Forbidden, NotFound):
                pass

    async def on_call(self, msg, args, **flags):
        if len(args) == 1:
            record = await self.bot.redis.get(f'join_message:{msg.guild.id}')
            if record:
                channel, _, join_message = record.partition(':')
                return f'Current join message: {join_message}\nChannel: **{channel}**'
            else:
                 return '{warning} Welcome message not set'

        manage_guild_perm = PermissionManageGuild()
        if not manage_guild_perm.check(msg.channel, msg.author):
            raise manage_guild_perm

        if args[1:].lower() in ('delete', 'remove'):
            await self.bot.redis.delete(f'join_message:{msg.guild.id}')
            return 'Welcome message removed'

        await self.bot.redis.set(f'join_message:{msg.guild.id}', f'{msg.channel.id}:{args[1:]}')
        await self.bot.delete_message(msg)
        await self.send(
            msg, delete_after=7,
            content='Set welcome message in this channel.'
        )