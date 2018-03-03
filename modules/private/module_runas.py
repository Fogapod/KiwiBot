from modules.modulebase import ModuleBase

from utils.helpers import find_user, get_string_after_entry

import re


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user> <message>'
    short_help = 'Force bot to think message was sent by selected user.'

    name = 'runas'
    aliases = (name, )
    guild_only = True
    arguments_required = 2
    protection = 2
    hidden = True

    async def on_call(self, msg, *args, **flags):
        user = await find_user(args[1], self.bot, guild=msg.guild, strict_guild=True)

        if user is None:
            return '{warning} User not found'

        guild_prefix = await self.bot.redis.get(f'guild_prefix:{msg.guild.id}')
        new_content = get_string_after_entry(args[1], msg.content)

        if guild_prefix is not None:
            new_content = guild_prefix + new_content
        else:
            new_content = self.bot.prefixes[0] + new_content

        msg.author = user
        msg.content = new_content
        await self.bot.on_message(msg)

        return f'Message processed as `{user.name}#{user.discriminator}`'