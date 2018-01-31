from utils.constants import ACCESS_LEVEL_NAMES


class ModuleBase(object):
    """Module is not documented"""

    name = 'module'
    keywords = ()
    arguments_required = 0
    protection = 0
    hidden = False
    disabled = False

    def __init__(self, bot):
        self.bot = bot

    @property
    def not_enough_arguments_text(self):
        return '{warning} Not enough arguments to call ' + self.name

    @property
    def permission_denied_text(self):
        return '{error} Access demied. Minimum access level to use command is `' + ACCESS_LEVEL_NAMES[self.protection] + '`'

    async def on_load(self):
        pass

    async def check_message(self, msg, *args):
        return args[0].lower() in self.keywords

    async def on_call(self, msg, *args):
        pass

    async def on_doc_request(self):
        return None

    async def on_unload(self):
        pass