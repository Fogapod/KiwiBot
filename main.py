import sys
import asyncio

from objects.bot import KiwiBot
from objects.logger import Logger

try:
    import uvloop
except ImportError:
    print('Failed to import uvloop. Is it installed?')
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


logger = Logger.get_logger()

bot = KiwiBot()
bot.run()

if bot.exit_code is not None:
    logger.debug(f'Exiting with code {bot.exit_code}')
    sys.exit(bot.exit_code)
