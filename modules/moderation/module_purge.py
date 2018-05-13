from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageMessages

from utils.funcs import find_user


DEF_LIMIT = 100
MAX_LIMIT = 500

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [target] [limit]'
    short_doc = 'Delete messages in channel'
    long_doc = (
        f'Target of prune can be: user mention/id/name, bots, users.\n'
        f'Default number of messages to check (limit) is {DEF_LIMIT}.\n'
        f'Maximum value is {MAX_LIMIT}.'
    )

    name = 'purge'
    aliases = (name, 'clear')
    category = 'Moderation'
    bot_perms  = (PermissionManageMessages(), )
    user_perms = (PermissionManageMessages(), )
    guild_only = True

    async def on_call(self, ctx, args, **flags):
        limit = None
        user_string = None

        if len(args) > 1:
            if args[-1].isdigit():
                limit = int(args[-1])
                if limit > MAX_LIMIT:
                    limit = MAX_LIMIT
                if len(args) > 2:
                    user_string = args[1:-1]

        if limit is None:
            limit = DEF_LIMIT
            user_string = args[1:]

        if len(args) == 1 or len(args) == 2 and user_string is None:
            check = lambda m: True
        elif user_string.lower() == 'bots':
            check = lambda m: m.author.bot
        elif user_string.lower() == 'users':
            check = lambda m: not m.author.bot
        else:
            user = await find_user(user_string, ctx.message, self.bot)
            if user is None:
                return '{error} User **' + user_string + '** not found!'
            check = lambda m: m.author.id == user.id

        deleted = await ctx.channel.purge(
            limit=limit, check=check,
            before=ctx.message.created_at
        )

        await ctx.send(
            f'Deleted {len(deleted)} messages from {", ".join(set("**" + str(m.author) + "**" for m in deleted))}' if deleted else 'No matched messages found',
            delete_after=7, register=False
        )

        await self.bot.delete_message(ctx.message)