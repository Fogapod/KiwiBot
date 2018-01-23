import time
import traceback

from discord import Client
from discord import Game

from commandmanager import CommandManager

from utils.constants import PREFIXES
from utils.formatters import format_response
from utils.config import Config


class BotMyBot(Client):

    def __init__(self, *args, **kwargs):
        super(BotMyBot, self).__init__(*args, **kwargs)
        self.config = Config('config.json', loop=self.loop)
        self.token = self.config['token']
        self.cm = CommandManager(self)
        self.cm.load_commands()

        self.recieved_messages_queue = {}

    def run(self, token=None):
        if token is None:
            token = self.token
        else:
            self.token = token

        super(BotMyBot, self).run(token)

    async def on_ready(self):
        print('Ready')

        previous_status = self.config.get('previous_status', '')
        if previous_status:
            await self.change_presence(game=Game(name=previous_status))

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.server is None:
            await self.send_message(message.channel, 'Personal messages are not supported yet')

        self.recieved_messages_queue[message.id] = (None, 5)

        lower_content = message.content.lower()

        if not lower_content.startswith(PREFIXES):
            return

        message.content = message.content[
            len(next(p for p in PREFIXES if lower_content.startswith(p))):]

        command_response = await self.cm.check_commands(message)

        if command_response:
            command_response = await format_response(command_response, message, self)

        if command_response:
            await self.send_message(message.channel, command_response)

    async def send_message(self, destination, *args, **kwargs):
        try:
            return await super(BotMyBot, self).send_message(destination, *args, **kwargs)
        except Exception:
            exception = traceback.format_exc()
            exception = '\n'.join(exception.split('\n')[-4:])
            exception = '❗ Message delivery failed\n```\n' + exception + '```'
            return await super(BotMyBot, self).send_message(destination, exception)


if __name__ == '__main__':
    BotMyBot().run()
