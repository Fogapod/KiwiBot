from objects.modulebase import ModuleBase
from objects.permissions import PermissionKickMembers

from utils.funcs import find_user, request_reaction_confirmation


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user> [reason]'
    short_doc = 'Kick user from server'

    name = 'kick'
    aliases = (name, )
    category = 'Moderation'
    min_args = 1
    guild_only = True
    bot_perms  = (PermissionKickMembers(), )
    user_perms = (PermissionKickMembers(), )

    async def on_call(self, msg, args, **flags):
        guild_member = await find_user(args[1], msg, self.bot, strict_guild=True)

        if not guild_member:
            return '{warning} User not found'

        reason = args[2:] or ''

        if guild_member == msg.guild.owner:
            return '{warning} Can\'t kick guild owner'
        if msg.guild.me.top_role <= guild_member.top_role:
            return '{warning} My top role is lower or equal to member\'s top role, can\'t kick'
        if msg.author.top_role <= guild_member.top_role and msg.guild.owner != msg.author:
            return '{warning} Your top role is lower or equal to member\'s top role, can\'t kick'

        kick_msg = await self.send(
            msg,
            content=(
                f'Are you sure you want to kick **{guild_member}** ?' +
                (f'\nReason:```\n{reason}```' if reason else '\n') +
                f'React with ✅ to continue'
            )
        )

        if await request_reaction_confirmation(kick_msg, msg.author, self.bot):
            kick_notification = await self.bot.send_message(
                guild_member,
                f'You were kicked from **{msg.guild.name}**\n' +
                (f'Reason:```\n{reason}```' if reason else 'No reason given')
            )
            try:
                await msg.guild.kick(
                    guild_member, reason=reason + f' kicked by {msg.author}')
            except Exception:
                await self.bot.delete_message(kick_notification)
                raise

            await self.bot.edit_message(
                kick_msg,
                content=(
                    f'Successefully kicked **{guild_member}** [{guild_member.id}]' +
                    (f'\nReason: ```\n{reason}```' if reason else '')
                )
            )
        else:
            await self.bot.edit_message(kick_msg, content=f'Cancelled kick of **{guild_member}**')