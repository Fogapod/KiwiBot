import discord
import logging


logging.basicConfig(level=logging.DEBUG)

class Bot(discord.Client):
    async def on_message(self, message):
        print('Recieved message:', message.content)

if __name__ == '__main__':
    print(discord.__version__)

    bot = Bot()
    bot.run('Mzk0NzkzNTc3MTYwMzc2MzIw.DUzD3Q.cgQdgHBlAaBYkptBIV59Y3tVb6I')
    print('Finished')

