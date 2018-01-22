import time
import traceback

from discord import Client

from commandmanager import CommandManager
from utils import PREFIXES, format_response


class BotMyBot(Client):

    def __init__(self, *args, **kwargs):
        super(BotMyBot, self).__init__(*args, **kwargs)
        self.token = 'token'
        self.cm = CommandManager(self)
        self.cm.load_commands()

    def run(self, token=None):
        if token is None:
            token = self.token
        super(BotMyBot, self).run(token)

    async def on_message(self, message):
        lower_content = message.content.lower()

        if not lower_content.startswith(PREFIXES):
            return

        message.content = message.content[
            len(next(p for p in PREFIXES if lower_content.startswith(p))):]

        command_response = await self.cm.check_commands(message)
        command_response = format_response(self, command_response)

        if command_response:
            await self.send_message(message.channel, command_response)

    async def send_message(self, destination, *args, **kwargs):
        try:
            await super(BotMyBot, self).send_message(destination, *args, **kwargs)
        except Exception:
            exception = traceback.format_exc()
            exception = '\n'.join(exception.split('\n')[-4:])
            exception = '❗ Message delivery failed\n```\n' + exception + '```'
            await super(BotMyBot, self).send_message(destination, exception)


if __name__ == '__main__':
    BotMyBot().run()
