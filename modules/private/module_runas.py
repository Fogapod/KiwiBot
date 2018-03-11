from modules.modulebase import ModuleBase

from permissions import PermissionBotOwner
from utils.helpers import find_user, get_local_prefix

import re


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user> <message>'
    short_doc = 'Force bot to think message was sent by selected user.'

    name = 'runas'
    aliases = (name, )
    guild_only = True
    required_args = 2
    require_perms = (PermissionBotOwner, )
    hidden = True

    async def on_call(self, msg, *args, **flags):
        user = await find_user(args[1], msg, self.bot, strict_guild=True)

        if user is None:
            return '{warning} User not found'

        prefix = await get_local_prefix(msg, self.bot)
        new_content = msg.content.partition(args[1])[2].lstrip()

        msg.author = user
        msg.content = prefix + new_content
        await self.bot.on_message(msg)

        return f'Message processed as `{user.name}#{user.discriminator}`'