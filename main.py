import time
import asyncio
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

        self.tracked_messages = {}

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

    async def on_message(self, message, from_edit=False):
        if message.author.bot:
            return

        if message.server is None:
            await self.send_message(
                message.channel, 'Personal messages are not supported yet')

        if not from_edit:
            await self.track_message(message)

        lower_content = message.content.lower()

        if not lower_content.startswith(PREFIXES):
            return

        message.content = message.content[
            len(next(p for p in PREFIXES if lower_content.startswith(p))):]

        command_response = await self.cm.check_commands(message)

        if command_response:
            command_response = await format_response(
                command_response, message, self)

        if command_response:
            await self.send_message(
                message.channel, command_response, response_to=message)

    async def on_message_edit(self, before, after):
        if before.id in self.tracked_messages:
            if self.tracked_messages[before.id] is not None:
                await self.delete_message(self.tracked_messages[before.id])
                self.tracked_messages[before.id] = None

            await self.on_message(after, from_edit=True)

    async def on_message_delete(self, message):
        if message.id in self.tracked_messages:
            if self.tracked_messages[message.id] is not None:
                await self.delete_message(self.tracked_messages[message.id])
                self.tracked_messages[message.id] = None


    async def send_message(self, destination, *args, response_to=None, **kwargs):
        try:
            message = await super(BotMyBot, self).send_message(
                destination, *args, **kwargs)
        except Exception:
            exception = traceback.format_exc()
            exception = '\n'.join(exception.split('\n')[-4:])
            exception = '❗ Message delivery failed\n```\n' + exception + '```'
            message = await super(BotMyBot, self).send_message(
                destination, exception)
        finally:
            if response_to is not None:
                await self.register_response(response_to, message)

            return message

    async def track_message(self, message):
        self.tracked_messages[message.id] = None
        self.loop.call_later(300, self.release_tracked_message, message.id)

    def release_tracked_message(self, message_id):
        del self.tracked_messages[message_id]

    async def register_response(self, request, response):
        if request.id in self.tracked_messages:
            self.tracked_messages[request.id] = response
        else:
            print('Request outdated, not registering')


if __name__ == '__main__':
    BotMyBot().run()
