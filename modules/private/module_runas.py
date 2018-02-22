from modules.modulebase import ModuleBase

import re


class Module(ModuleBase):
    """{prefix}{keywords} <user> <message>
    
    Force bot to think message was sent by selected user.
    {protection} or higher permission level required to use"""

    name = 'runas'
    keywords = (name, )
    arguments_required = 1
    protection = 2

    async def on_call(self, msg, *args, **options):
        user_id = re.match('(<@!?)?(\d{18})>?$', args[1]).groups()[1]
        user = msg.guild.get_member(int(user_id))
        
        if user is None:
            return '{warning} User not found'

        new_content = msg.content[msg.content.index(args[1]) + len(args[1]):].strip()
        msg.author = user
        msg.content = self.bot.prefixes[0] + new_content
        
        await self.bot.on_message(msg)
        
        return 'Message processed as `' + user_id + '`'