from objects.modulebase import ModuleBase

from utils.funcs import find_user


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user>'
    short_doc = 'Get matched users list.'

    name = 'users'
    aliases = (name, 'userlist')
    required_args = 1

    async def on_call(self, msg, *args, **flags):
        users = await find_user(
            msg.content.partition(args[0])[2].lstrip(),
            msg, self.bot, max_count=20
        )

        if not users:
            return '{warning} Users not found'

        return 'Matched users:```\n' + '\n'.join(f'{str(i + 1) + ")":<3}{str(u):<37} {u.id}' for i, u in enumerate(users)) + '```'