from commands.commandbase import CommandBase


class Command(CommandBase):
    """{prefix}{keywords}
    
    Get bot invite link.
    {protection} or higher permission level required to use"""

    name = 'invite'
    keywords = (name, )
    arguments_required = 0
    protection = 0

    async def on_call(self, message):
    	return 'Invite me to your server by this link: https://discordapp.com/api/oauth2/authorize?client_id=394793577160376320&permissions=1141172288&scope=bot\nContact developar: https://discord.gg/TNXn8R7'