from objects.modulebase import ModuleBase
from objects.permissions import PermissionBanMembers

from utils.funcs import find_user, request_reaction_confirmation

from discord import Member


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user> [reason]'
    short_doc = 'Ban user on server'

    name = 'ban'
    aliases = (name, 'hackban')
    category = 'Moderation'
    min_args = 1
    guild_only = True
    bot_perms  = (PermissionBanMembers(), )
    user_perms = (PermissionBanMembers(), )

    async def on_call(self, ctx, args, **flags):
        user = await find_user(args[1], ctx.message)

        if not user:
            return '{warning} User not found'
        reason = args[2:] or ''

        if isinstance(user, Member):
            if user == ctx.guild.owner:
                return '{warning} Can\'t ban guild owner'
            if ctx.me.top_role <= user.top_role:
                return '{warning} My top role is lower or equal to member\'s top role, can\'t ban'
            if ctx.author.top_role <= user.top_role and ctx.author != ctx.guild.owner:
                return '{warning} Your top role is lower or equal to member\'s top role, can\'t ban'

        ban_msg = await ctx.send(
            (
                f'Are you sure you want to ban **{user}** ?' +
                (f'\nReason:```\n{reason}```' if reason else '\n') +
                f'React with ✅ to continue'
            )
        )

        if await request_reaction_confirmation(ban_msg, ctx.author):
            ban_notification = await self.bot.send_message(
                user,
                f'You were banned on **{ctx.guild.name}**\n' +
                (f'Reason:```\n{reason}```' if reason else 'No reason given')
            )
            try:
                await ctx.guild.ban(
                    user, delete_message_days=0,
                    reason=reason + f' banned by {ctx.author}'
                )
            except Exception:
                await self.bot.delete_message(ban_notification)
                raise

            await self.bot.edit_message(
                ban_msg,
                content=(
                    f'Successefully banned **{user}** [{user.id}]' +
                    (f'\nReason: ```\n{reason}```' if reason else '')
                )
            )
        else:
            await self.bot.edit_message(ban_msg, content=f'Cancelled ban of **{user}**')