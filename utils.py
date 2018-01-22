AUTHOR_ID = '253384991940149249'
BOT_ID    = '394793577160376320'

PREFIXES = ('+', 'w!', '<@' + str(BOT_ID) + '>')

ACCESS_LEVEL_NAMES = {3: 'BOT_OWNER', 2: 'SERVER_OWNER', 1: 'SERVER_ADMIN', 0: 'USER'}


def format_response(bot, response):
	return response