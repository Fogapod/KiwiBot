from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks, PermissionExternalEmojis

from utils.funcs import find_user, _get_last_user_message_timestamp

from discord import Embed, Colour, Member

from datetime import datetime


STATUS_EMOTES = {
    'online':    '<:online:427209268240973854>',
    'idle':      '<:idle:427209268203094017>',
    'dnd':       '<:dnd:427209268043841537>',
    'offline':   '<:offline:427209267687194625>',
    'invisible': '<:invisible:427209267687194625>'
}

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [user]'
    short_doc = 'Get information about given user'

    name = 'user'
    aliases = (name, 'userinfo')
    category = 'Discord'
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **flags):
        if len(args) == 1:
            user = ctx.author
        else:
            user = await find_user(args[1:], ctx.message)

        if user is None:
            return await ctx.warn('User not found')

        e = Embed(title=str(user), url=user.avatar_url, colour=Colour.gold())
        e.set_thumbnail(url=user.avatar_url)
        e.add_field(
            name='registered', inline=False,
            value=f'`{user.created_at.replace(microsecond=0)}` ({(datetime.now() - user.created_at).days} days ago)'
        )
        if isinstance(user, Member):
            # function can return members from different guild
            if user.guild == ctx.guild:
                e.title += ' (member)'
                e.add_field(
                    name='member since', inline=False,
                    value=f'`{user.joined_at.replace(microsecond=0)}` ({(datetime.now() - user.joined_at).days} days)'
                )
                last_msg_ts = _get_last_user_message_timestamp(user.id, ctx.channel.id)
                if last_msg_ts != datetime.fromtimestamp(0):
                    last_msg_ts = last_msg_ts.replace(microsecond=0)
                    e.add_field(
                        name='last message sent', inline=False,
                        value=f'`{last_msg_ts}`'
                    )
                e.add_field(name='top role', value=user.top_role.mention)
                e.add_field(name='total roles', value=len(user.roles))

                if user.nick is not None:
                    e.add_field(name='nick', value=user.nick, inline=False)

            external_emoji_perm = PermissionExternalEmojis().check(ctx.channel, self.bot.user)

            if user.activity is None:
                e.add_field(
                    name='status',
                    value=(STATUS_EMOTES[str(user.status)] if external_emoji_perm else '') + str(user.status)
                )
            else:
                e.add_field(
                    name='activity',
                    value=(STATUS_EMOTES[str(user.status)] if external_emoji_perm else '') + f'**{user.activity.type.name}** {user.activity.name}'
                )

        e.add_field(name='robot', value='yes' if user.bot else 'no')
        e.set_footer(text=user.id)

        await ctx.send(embed=e)
