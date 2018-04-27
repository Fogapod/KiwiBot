from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageGuild


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [set|remove] [prefix]'
    short_doc = 'Change bot guild prefix.'

    name = 'prefix'
    aliases = (name, )
    guild_only = True

    async def on_call(self, msg, args, **flags):
        if len(args) == 1:
            prefix = await self.bot.redis.get(f'guild_prefix:{msg.guild.id}')

            if not prefix:
                return '{warning} Custom prefix not set'
            else:
                return f'Prefix for this guild is: **{prefix}**'

        manage_guild_perm = PermissionManageGuild()
        if not manage_guild_perm.check(msg.channel, msg.author):
            raise manage_guild_perm

        if args[1:].lower() in ('remove', 'delete', 'clear', 'del', 'rem'):
            await self.bot.redis.delete(f'guild_prefix:{msg.guild.id}')
            del self.bot._guild_prefixes[msg.guild.id]
            return 'Guild prefix override removed'

        if len(args) < 3:
            return await self.on_not_enough_arguments(msg)

        if args[1].lower() == 'set':
            prefix = args[2:][:20]  # 20 characters limit
            await self.bot.redis.set(f'guild_prefix:{msg.guild.id}', prefix)
            self.bot._guild_prefixes[msg.guild.id] = prefix
            return f'Guild prefix set to: **{prefix}**'

        return await self.on_not_enough_arguments(msg)