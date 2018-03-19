from objects.modulebase import ModuleBase
from objects.permissions import PermissionBanMembers

from utils.funcs import find_user, request_reaction_confirmation

from discord import Member


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user> [reason]'
    short_doc = 'Ban user.'

    name = 'ban'
    aliases = (name, 'hackban')
    required_args = 1
    guild_only = True
    require_perms  = (PermissionBanMembers, )
    required_perms = (PermissionBanMembers, )

    async def on_call(self, msg, *args, **flags):
        user = await find_user(args[1], msg, self.bot)

        if not user:
            return '{warning} User not found'
        reason = msg.content[len(args[0]):].partition(args[1])[2].lstrip() or f'performed by {msg.author} [{msg.author.id}]'

        if isinstance(user, Member):
            if user == msg.guild.owner:
                return '{warning} Can\'t ban guild owner'
            if msg.guild.me.top_role <= user.top_role:
                return '{warning} My top role is lower or equal to member\'s top role, can\'t ban'
            if msg.author.top_role <= user.top_role:
                return '{warning} Your top role is lower or equal to member\'s top role, can\'t ban'

        ban_msg = await self.send(
            msg,
            content=(
                f'Are you sure you want to ban **{user}** ?' +
                (f'\nReason:```\n{reason}```' if reason else '\n') +
                f'React with ✅ to continue'
            )
        )

        if await request_reaction_confirmation(ban_msg, msg.author, self.bot):
            await msg.guild.ban(user, reason=reason, delete_message_days=0)
            await self.bot.edit_message(
                ban_msg,
                content=(
                    f'Successefully banned **{user}** [{user.id}]' +
                    (f'\nReason: ```\n{reason}```' if reason else '')
                )
            )
        else:
            await self.bot.edit_message(ban_msg, content=f'Cancelled ban of **{user}** [{user.id}]')