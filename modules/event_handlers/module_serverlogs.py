from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageGuild

from utils.formatters import lazy_format


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [channel]'
    short_doc = 'Enables/disables logging. Useful for moderation.'

    name = 'serverlogs'
    aliases = (name, 'slogs')
    require_perms = (PermissionManageGuild(), )
    guild_only = True

    async def on_load(self, from_reload):
        self.events = {
            'command_use': self.on_command_use,
            'member_join': self.on_member_join,
            'member_remove': self.on_member_leave
        }

    async def get_logging_channel(self, guild):
        channel_id = await self.bot.redis.get(f'serverlogs:{guild.id}')
        if channel_id:
            return guild.get_channel(int(channel_id))

    async def log(self, channel, text, **kwargs):
        await self.bot.send_message(channel, content=text, **kwargs)

    async def on_command_use(self, module, msg, args):
        channel = await self.get_logging_channel(msg.guild)
        if not channel:
            return

        await self.log(
            channel,
            f'**{msg.author}**-`{msg.author.id}` used command **{module.name}** in channel {msg.channel.mention}'
        )

    async def on_member_join(self, member):
        channel = await self.get_logging_channel(member.guild)
        if not channel:
            return

        await self.log(channel, f'**{member}**-`{member.id}` joined guild')

    async def on_member_leave(self, member):
        channel = await self.get_logging_channel(member.guild)
        if not channel:
            return

        await self.log(channel, f'**{member}**-`{member.id}` left guild')

    async def on_call(self, msg, args, **flags):
        if len(args) == 1:
            channel = msg.channel
        else:
            channel = await find_channel(args[1:], msg.guild, self.bot)
            if channel is None:
                return '{warning} Channel not found'

        log_channel_id = await self.bot.redis.get(f'serverlogs:{msg.guild.id}')

        if log_channel_id and msg.guild.get_channel(int(log_channel_id)) == msg.channel:
            await self.bot.redis.delete(f'serverlogs:{msg.guild.id}')
            return f'Disabled logs in {channel.mention}'
        else:
            await self.bot.redis.set(f'serverlogs:{msg.guild.id}', str(channel.id))
            return f'Enabled logs in {channel.mention}'