from utils.constants import ACCESS_LEVEL_NAMES
from utils.checks import get_user_access_level


class ModuleBase:
    """Module is not documented"""

    name = 'module'
    keywords = ()
    arguments_required = 0
    protection = 0
    hidden = False
    disabled = False

    def __init__(self, bot):
        self.bot = bot

    def check_argument_count(self, argc):
        return argc - 1 >= self.arguments_required

    async def check_permissions(self, message):
        return await get_user_access_level(message) >= self.protection

    @property
    def not_enough_arguments_text(self):
        return '{warning} Not enough arguments to call ' + self.name

    @property
    def permission_denied_text(self):
        return '{error} Access demied. Minimum access level to use command is `' + ACCESS_LEVEL_NAMES[self.protection] + '`'

    async def on_load(self):
        pass

    async def check_message(self, msg, *args, **options):
        if self.disabled:
            return False
        return await self.on_check_message(msg, *args, **options)

    async def on_check_message(self, msg, *args, **options):
        return args[0].lower() in self.keywords

    async def call_command(self, msg, *args, **options):
        return await self.on_call(msg, *args, **options)

    async def on_call(self, msg, *args, **options):
        pass

    async def on_doc_request(self):
        return None

    async def on_unload(self):
        pass