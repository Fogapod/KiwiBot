from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageMessages

from utils.funcs import find_user


DEF_LIMIT = 100
MAX_LIMIT = 1000

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [target] [limit]'
    short_doc = 'Delete messages in channel.'
    additional_doc = (
        f'Target of prune can be: user mention/id/name, bots, users.\n'
        f'Default number of messages to check (limit) is {DEF_LIMIT}.\n'
        f'Maximum value is {MAX_LIMIT}.'
    )

    name = 'purge'
    aliases = (name, 'clear')
    require_perms  = (PermissionManageMessages(), )
    required_perms = (PermissionManageMessages(), )
    guild_only = True

    async def on_call(self, msg, args, **flags):
        limit = None
        user_string = None

        if len(args) > 1:
            if args[-1].isdigit():
                limit = int(args[-1])
                if limit > 1000:
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
            user = await find_user(user_string, msg, self.bot)
            if user is None:
                return '{error} User **' + user_string + '** not found!'
            check = lambda m: m.author.id == user.id

        deleted = await msg.channel.purge(
            limit=limit, check=check,
            before=msg.created_at
        )

        await msg.channel.send(
            f'Deleted {len(deleted)} messages from {" ".join(set("**" + str(m.author) + "**" for m in deleted))}' if deleted else 'No matched messages found',
            delete_after=7
        )

        await msg.delete()