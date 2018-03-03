from modules.modulebase import ModuleBase

from utils.helpers import find_user, get_string_after_entry

import re


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user> <message>'
    short_help = 'Force bot to think message was sent by selected user.'

    name = 'runas'
    aliases = (name, )
    guild_only = True
    arguments_required = 1
    protection = 2
    hidden = True

    async def on_call(self, msg, *args, **flags):
        user = await find_user(args[1], self.bot, guild=msg.guild, strict_guild=True)

        if user is None:
            return '{warning} User not found'

        new_content = get_string_after_entry(args[1], msg.content)
        msg.author = user
        msg.content = self.bot.prefixes[0] + new_content
        print(msg.content)
        
        await self.bot.on_message(msg)
        
        return f'Message processed as `{user.name}#{user.discriminator}`'