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

        self.recieved_messages_queue = {}
        self.loop.create_task(self.recieved_messages_queue_background_cleaner())

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
            await self.send_message(
                message.channel, 'Personal messages are not supported yet')

        if message.id not in self.recieved_messages_queue:
            self.recieved_messages_queue[message.id] = [None, 5]

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
        if before.id in self.recieved_messages_queue:
            if self.recieved_messages_queue[before.id][0] is not None:
                await self.delete_message(
                    self.recieved_messages_queue[before.id][0])
                self.recieved_messages_queue[before.id][0] = None
            await self.on_message(after)

    async def on_message_delete(self, message):
        if message.id in self.recieved_messages_queue:
            if self.recieved_messages_queue[message.id][0] is not None:
                await self.delete_message(
                    self.recieved_messages_queue[message.id][0])
                self.recieved_messages_queue[message.id][0] = None


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

    async def register_response(self, request, response):
        if request.id in self.recieved_messages_queue:
            self.recieved_messages_queue[request.id][0] = response
        else:
            print('Request outdated, not registering')

    async def recieved_messages_queue_background_cleaner(self):
        await self.wait_until_ready()
        while not self.is_closed:
            for mid, [response, timer] in self.recieved_messages_queue.copy().items():
                if timer == 0:
                    del self.recieved_messages_queue[mid]
                else:
                    self.recieved_messages_queue[mid][1] -= 1

            await asyncio.sleep(60)


if __name__ == '__main__':
    BotMyBot().run()
