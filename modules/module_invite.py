from modules.modulebase import ModuleBase


class Module(ModuleBase):
    
    short_doc = 'Get bot invite link.'

    name = 'invite'
    aliases = (name, )

    async def on_call(self, msg, *args, **options):
        return 'Invite me to your server by this link: <https://discordapp.com/oauth2/authorize?client_id=394793577160376320&scope=bot&permissions=8>\nContact developar: https://discord.gg/TNXn8R7'