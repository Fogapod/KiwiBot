from modules.modulebase import ModuleBase

from utils.helpers import find_user


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user>'
    short_doc = 'Get matched users list.'

    name = 'user2'
    aliases = (name, )
    hidden = True

    async def on_call(self, msg, *args, **flags):
        if len(args) == 1:
            users = (msg.author, )
        else:
            users = await find_user(
                msg.content.partition(args[0])[2].lstrip(),
                msg, self.bot, max_count=20
            )

        if not users:
            return '{warning} Users not found'

        return 'Matched users:```\n' + '\n'.join(f'{str(i + 1) + ")":<3}{str(u):<20} {u.id}' for i, u in enumerate(users)) + '```'