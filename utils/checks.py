from utils.constants import AUTHOR_ID


async def get_user_access_level(message):
    if message.author.id == AUTHOR_ID:
    	return 2
    elif message.author.permissions_in(message.channel).administrator:
    	return 1
    else:
    	return 0