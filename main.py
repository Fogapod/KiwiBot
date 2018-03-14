import sys

from objects.bot import BotMyBot
from objects.logger import Logger


logger = Logger.get_logger()

bot = BotMyBot()
bot.run()

if bot.exit_code is not None:
    logger.debug(f'Exiting with code {bot.exit_code}')
    sys.exit(bot.exit_code)