from modules.modulebase import ModuleBase

from utils.helpers import find_user_in_guild, get_string_after_entry

import re


class Module(ModuleBase):
    """{prefix}{keywords} <user> <message>

    Force bot to think message was sent by selected user.
    {protection} or higher permission level required to use"""

    name = 'runas'
    keywords = (name, )
    arguments_required = 1
    protection = 2
    hidden = True

    async def on_call(self, msg, *args, **options):
        member = None
        id_match = re.fullmatch('(<@!?)?(\d{18})>?', args[1])

        if id_match is None:
            member = await find_user_in_guild(args[1], msg.guild, self.bot)
        else:
            member = msg.guild.get_member(int(id_match.group(2)))

        if member is None:
            return '{warning} Member not found'

        new_content = get_string_after_entry(args[1], msg.content)
        msg.author = member
        msg.content = self.bot.prefixes[0] + new_content
        
        await self.bot.on_message(msg)
        
        return 'Message processed as `' + str(member.name) + '#' + member.discriminator + '` '