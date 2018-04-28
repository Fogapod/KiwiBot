from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageGuild


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [prefix]'
    short_doc = 'Change bot guild prefix.'
    additional_doc = (
        'Subcommands:\n'
        '\t{prefix}{aliases} [delete|remove|clear] - remove guild prefix'
    )

    name = 'prefix'
    aliases = (name, )
    guild_only = True

    async def on_call(self, msg, args, **flags):
        if len(args) == 1:
            prefix = await self.bot.redis.get(f'guild_prefix:{msg.guild.id}')

            if not prefix:
                return 'Custom prefix not set. Default is: **' + self.bot._default_prefix + '**'
            else:
                return f'Prefix for this guild is: **{prefix}**'

        manage_guild_perm = PermissionManageGuild()
        if not manage_guild_perm.check(msg.channel, msg.author):
            raise manage_guild_perm

        if args[1:].lower() in ('remove', 'delete', 'clear'):
            await self.bot.redis.delete(f'guild_prefix:{msg.guild.id}')
            del self.bot._guild_prefixes[msg.guild.id]
            return 'Guild prefix removed'

        prefix = args[1:][:200]  # 200 characters limit
        await self.bot.redis.set(f'guild_prefix:{msg.guild.id}', prefix)
        self.bot._guild_prefixes[msg.guild.id] = prefix.lower()

        return f'Guild prefix set to: **{prefix}**'