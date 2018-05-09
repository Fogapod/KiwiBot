from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from utils.funcs import find_role

from discord import Embed

from datetime import datetime


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <role>'
    short_doc = 'Get information about given role'

    name = 'role'
    aliases = (name, 'roleinfo')
    category = 'Discord'
    bot_perms = (PermissionEmbedLinks(), )
    min_args = 1
    guild_only = True

    async def on_call(self, msg, args, **flags):
        role = await find_role(args[1:], msg.guild, self.bot)

        if role is None:
            return '{warning} Role not found'

        e = Embed(colour=role.colour, title=role.name)
        e.add_field(
            name='Created', value=f'`{role.created_at.replace(microsecond=0)}`')
        e.add_field(
            name='Position', value=f'{len(msg.guild.roles) - role.position}/{len(msg.guild.roles)}')
        e.add_field(name='Members', value=len(role.members))
        e.add_field(name='Permission bitfield', value=role.permissions.value)
        e.add_field(name='Colour', value=f'#{role.colour.value:06x}')
        e.add_field(name='Mentionable', value=role.mentionable)
        e.set_footer(text=role.id)

        await self.send(msg, embed=e)