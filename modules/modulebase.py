from utils.constants import ACCESS_LEVEL_NAMES
from utils.checks import get_user_access_level


class ModuleBase:

    usage_doc = '{prefix}{aliases}'
    short_doc = 'Not documented'
    additional_doc = ''
    permission_doc = '{protection} or higher permission level required to use'

    name = 'module'
    aliases = ()
    arguments_required = 0
    protection = 0
    hidden = False
    disabled = False

    def __init__(self, bot):
        self.bot = bot

    def check_argument_count(self, argc, msg):
        return argc - 1 >= self.arguments_required

    async def check_permissions(self, msg):
        return await get_user_access_level(msg) >= self.protection

    async def on_not_enough_arguments(self, msg):
        return '{error} Not enough arguments to call ' + self.name

    async def on_permission_denied(self, msg):
        return '{error} Access demied. Minimum access level to use command is `' + ACCESS_LEVEL_NAMES[self.protection] + '`'

    async def on_load(self, from_reload):
        pass

    async def check_message(self, msg, *args, **flags):
        if self.disabled:
            return False
        return await self.on_check_message(msg, *args, **flags)

    async def on_check_message(self, msg, *args, **flags):
        return args[0].lower() in self.aliases

    async def call_command(self, msg, *args, **flags):
        return await self.on_call(msg, *args, **flags)

    async def on_call(self, msg, *args, **flags):
        pass

    async def on_message_edit(self, before, after, *args, **flags):
        pass

    async def on_message_delete(self, msg, *args, **flags):
        pass

    async def on_doc_request(self):
        return None

    async def on_error(self, tb_text, msg):
        return (
            '{error} Error appeared during execution '
            + self.name
            + '```\n' + '\n'.join(tb_text.split('\n')[-4:]) + '\n```'
        )

    async def on_unload(self):
        pass