from modules.modulebase import ModuleBase

from permissions import PermissionKickMembers

from utils.helpers import find_user, request_reaction_confirmation


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user> [reason]'
    short_doc = 'Kick user from server.'

    name = 'kick'
    aliases = (name, )
    required_args = 1
    guild_only = True
    require_perms  = (PermissionKickMembers, )
    required_perms = (PermissionKickMembers, )

    async def on_call(self, msg, *args, **flags):
        guild_member = await find_user(args[1], msg, self.bot, strict_guild=True)

        if not guild_member:
            return '{warning} User not found'

        reason = msg.content[len(args[0]):].partition(args[1])[2].lstrip() or None

        if msg.guild.me.top_role <= guild_member.top_role:
            return '{warning} My top role is lower or equal to member\'s top role, can\'t kick'
        if msg.author.top_role <= guild_member.top_role:
            return '{warning} Your top role is lower or equal to member\'s top role, can\'t kick'

        kick_msg = await self.send(
            msg,
            content=(
                f'Are you sure you want to kick **{guild_member}**?' +
                (f'\nReason:```\n{reason}```' if reason else '\n') +
                f'React with ✅ to continue'
            )
        )

        if await request_reaction_confirmation(kick_msg, msg.author, self.bot):
            await msg.guild.kick(guild_member, reason=reason)
            await self.bot.edit_message(
                kick_msg,
                content=(
                    f'Successefully kicked **{guild_member}** [{guild_member.id}]' +
                    (f'\nReason: `{reason}`' if reason else '')
                )
            )
        else:
            await self.bot.edit_message(kick_msg, content=f'Cancelled kick of **{guild_member}** [{guild_member.id}]')