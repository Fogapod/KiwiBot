from modules.modulebase import ModuleBase


class Module(ModuleBase):
    """{prefix}{keywords}
    
    Get bot invite link.
    {protection} or higher permission level required to use"""

    name = 'invite'
    keywords = (name, )
    arguments_required = 0
    protection = 0

    async def on_call(self, message, *args):
    	return 'Invite me to your server by this link: ​<https://discordapp.com/oauth2/authorize?client_id=394793577160376320&scope=bot&permissions=8>\nContact developar: https://discord.gg/TNXn8R7'