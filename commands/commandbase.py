# coding:utf8

class CommandBase(object):
    """Command is not documented"""

    name = 'plugin'
    keywords = (name, )
    arguments_required = 0
    protection = 0
    disabled = False

    def __init__(self, bot):
        self.bot = bot

    def on_load(self):
        pass

    async def check_message(self, msg):
        return msg.content.split()[0].lower() in self.keywords

    async def on_call(self, msg):
        pass

    async def on_doc_request(self):
        return False

    def on_exit(self):
        pass