# coding:utf8

class CommandBase(object):
    """Command is not documented"""

    name = 'command'
    keywords = (name, )
    arguments_required = 0
    protection = 0
    disabled = False

    def __init__(self, bot):
        self.bot = bot

    @property
    def not_enough_arguments_text(self):
        return '{warning} Not enough arguments to call ' 

    @property
    def permission_denied_text(self):
        return '{error} Access demied. Minimum access level to use command is `' + self.protection + '`'

    def on_load(self):
        pass

    async def check_message(self, msg):
        return msg.content.split()[0].lower() in self.keywords

    async def on_call(self, msg):
        pass

    async def on_doc_request(self):
        return None

    def on_exit(self):
        pass