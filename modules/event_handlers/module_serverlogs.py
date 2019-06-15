from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageGuild

from io import BytesIO

from utils.funcs import find_channel
from utils.formatters import replace_mass_mentions, trim_text

from discord import File


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [channel]'
    short_doc = 'Enables/disables logging. Useful for moderation'

    name = 'serverlogs'
    aliases = (name, 'slogs')
    category = 'Moderation'
    user_perms = (PermissionManageGuild(), )
    guild_only = True

    async def on_load(self, from_reload):
        self.events = {
            'command_use':    self.on_command_use,
            'member_join':    self.on_member_join,
            'member_remove':  self.on_member_leave,
            'message_delete': self.on_message_delete,
            'message_edit':   self.on_message_edit,
            'member_update':  self.on_member_update
        }

    async def get_logging_channel(self, guild):
        if guild is None:
            return

        channel = None
        channel_id = await self.bot.redis.get(f'serverlogs:{guild.id}')

        if channel_id:
            channel = guild.get_channel(int(channel_id))
            if channel is None:  # channel deleted
                await self.bot.redis.delete(f'serverlogs:{guild.id}')

        return channel

    async def log(self, channel, text, **kwargs):
        text = trim_text(replace_mass_mentions(text))
        await self.bot.send_message(channel, text, **kwargs)

    async def on_command_use(self, module, ctx, args):
        channel = await self.get_logging_channel(ctx.guild)
        if not channel:
            return

        await self.log(
            channel,
            f'**{ctx.author}**-`{ctx.author.id}` used command **{module.name}** in {ctx.channel.mention}'
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

    async def on_message_delete(self, msg):
        if msg.author.id == self.bot.user.id:
            return

        channel = await self.get_logging_channel(msg.guild)
        if not channel:
            return

        content = f'```\n{msg.content}```' if msg.content else ''
        content = f'🗑 Message by **{msg.author}** deleted in {msg.channel.mention}{content}'

        await self.log(
            channel, content, embed=msg.embeds[0] if msg.embeds else None,
            files=[File(BytesIO(await (await self.bot.sess.get(a.url)).read()), filename=a.filename) for a in msg.attachments]
        )

    async def on_message_edit(self, before, after):
        if after.author.id == self.bot.user.id:
            return

        if before.content == after.content:
            return  # pin/unpin or embed update

        channel = await self.get_logging_channel(after.guild)
        if not channel:
            return

        before_content = f'Old```\n{before.content}```' if before.content else ''
        after_content = f'New```\n{after.content}```' if after.content else ''
        content = f'📝 **{after.author}** edited message `{after.id}` in {after.channel.mention}\n{before_content}{after_content}'

        await self.log(channel, content)

    async def on_member_update(self, before, after):
        channel = await self.get_logging_channel(after.guild)
        if not channel:
            return

        if str(before) != str(after):  # name or discriminator updated
            await self.log(channel, f'🔎 Member updated: **{before}** -> **{after}**')

    async def on_call(self, ctx, args, **flags):
        if len(args) == 1:
            channel = ctx.channel
        else:
            channel = await find_channel(
                args[1:], ctx.guild,
                include_voice=False, include_category=False
            )
            if channel is None:
                return await ctx.error('Channel not found')

        log_channel_id = await self.bot.redis.get(f'serverlogs:{ctx.guild.id}')

        if log_channel_id and ctx.guild.get_channel(int(log_channel_id)) == ctx.channel:
            await self.bot.redis.delete(f'serverlogs:{ctx.guild.id}')
            return f'Disabled logs in {channel.mention}'
        else:
            await self.bot.redis.set(f'serverlogs:{ctx.guild.id}', str(channel.id))
            return f'Enabled logs in {channel.mention}'
