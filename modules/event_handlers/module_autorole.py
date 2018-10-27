from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageRoles

from utils.funcs import find_role

from discord import Embed, Colour, Forbidden, NotFound


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [add|remove] [role]'
    short_doc = 'Allows to set or remove autorole(s)'
    long_doc = (
        'See current autoroles:\n'
        '\t{prefix}{aliases}\n\n'
        'Add autorole:\n'
        '\t{prefix}{aliases} [add|set] <role>\n\n'
        'Remove autorole:\n'
        '\t{prefix}{aliases} [remove|delete] <role>\n\n'
        'Command flags:\n'
        '\t[--bots|-b]: assign role only to bots if set, otherwise only humans'
    )

    name = 'autorole'
    aliases = (name, 'autoroles')
    category = 'Moderation'
    bot_perms = (PermissionManageRoles(), )
    user_perms = (PermissionManageRoles(), )
    flags = {
        'bots': {
            'alias': 'b',
            'bool': True
        }
    }
    guild_only = True

    async def on_load(self, from_reload):
        self.events = {
            'member_join': self.on_member_join
        }

    async def on_member_join(self, member):
        if member.bot:
            roles = await self.bot.redis.smembers(f'autorole_bots:{member.guild.id}')
            bots = True
        else:
            roles = await self.bot.redis.smembers(f'autorole:{member.guild.id}')
            bots = False

        for role in roles:
            try:
                await self.bot.http.add_role(member.guild.id, member.id, int(role))
            except NotFound as e:
                if 'role' in str(e).lower():  # make sure that role isn't found, not user
                    if bots:
                        await self.bot.redis.srem(f'autorole_bots:{member.guild.id}', role)
                    else:
                        await self.bot.redis.srem(f'autorole:{member.guild.id}', role)
            except Forbidden:
                pass

    async def on_call(self, ctx, args, **flags):
        if len(args) == 1:
            human_roles = await self.bot.redis.smembers(f'autorole:{ctx.guild.id}')
            bot_roles = await self.bot.redis.smembers(f'autorole_bots:{ctx.guild.id}')
            
            if not (human_roles or bot_roles):
                return await ctx.warn('No autoroles set')

            e = Embed(colour=Colour.gold(), title='Guild autoroles')
            if human_roles:
                e.add_field(name='Humans', value=', '.join(f'<@&{r}>' for r in human_roles))
            if bot_roles:
                e.add_field(name='Robots', value=', '.join(f'<@&{r}>' for r in bot_roles))

            return await ctx.send(embed=e)

        if len(args) < 3:
            return await self.on_not_enough_arguments(ctx)

        bot_flag = flags.get('bots')

        if args[1].lower() in ('set', 'add'):
            role = await find_role(args[2:], ctx.guild, self.bot)
            if role is None:
                return await ctx.error('Role not found')

            if role.position >= ctx.author.top_role.position:
                if not ctx.author == ctx.guild.owner:
                    return await ctx.error('Role is higher or equal to your top role')
            if role.permissions > ctx.author.guild_permissions:
                return await ctx.error('Role has higher permissions than you in guild')
            if role.position >= ctx.guild.me.top_role.position:
                return await ctx.error('Role is higher or equal to my top role, I won\'t be able to assign it')

            if bot_flag:
                await self.bot.redis.sadd(f'autorole_bots:{ctx.guild.id}', str(role.id))
            else:
                await self.bot.redis.sadd(f'autorole:{ctx.guild.id}', str(role.id))
            
            return f'Set {role.mention} as autorole' + (' for bots' if bot_flag else '')

        if args[1].lower() in ('delete', 'remove'):
            role = await find_role(args[2:], ctx.guild, self.bot)
            if role is None:
                return await ctx.error('Role not found')

            if bot_flag:
                await self.bot.redis.srem(f'autorole_bots:{ctx.guild.id}', str(role.id))
            else:
                await self.bot.redis.srem(f'autorole:{ctx.guild.id}', str(role.id))

            return f'Removed {role.mention} autorole' + (' for bots' if bot_flag else '')

        return await self.on_not_enough_arguments(ctx)
