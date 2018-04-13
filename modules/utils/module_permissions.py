from objects.modulebase import ModuleBase

from utils.funcs import find_role, find_user

from discord import Permissions


PERM_MISSING = '❌'
PERM_THERE   = '✅'



class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [member|role]'
    short_doc = 'Show list of member or role permissions.'
    additional_doc = (
        'Available flags:\n'
        '\tt: show permissions set to true only\n'
        '\tf: show permissions set to false only\n'
        '\tg or global: show guild permissions'
    )

    name = 'permissions'
    aliases = (name, 'perms')
    call_flags = {
        't': {
            'bool': True
        },
        'f': {
            'bool': True
        },
        'global': {
            'alias': 'g',
            'bool': True
        }
    }
    guild_only = True

    async def on_call(self, msg, args, **flags):
        only_true  = flags.get('t', False)
        only_false = flags.get('f', False)
        use_global = flags.get('global', False)

        if only_true and only_false:
            return '{error} t and f flags conflict'

        if len(args) == 1:
            if use_global:
                permissions = msg.author.guild_permissions
            else:
                permissions = msg.channel.permissions_for(msg.author)
            target = str(msg.author)
        else:
            member = await find_user(args[1:], msg, self.bot, strict_guild=True)
            if member is not None:
                if use_global:
                    permissions = member.guild_permissions
                else:
                    permissions = msg.channel.permissions_for(member)
                target = str(member)
            else:
                role = await find_role(args[1:], msg.guild, self.bot)

                if role is None:
                    return '{warning} Role or member not found'

                permissions = role.permissions
                target = str(role)

                if use_global:
                    if permissions.administrator:
                        permissions = Permissions.all()
                elif permissions.administrator:
                    permissions = Permissions(Permissions.all().value & ~Permissions.voice().value)
                else:
                    for k, v in msg.channel.overwrites_for(role):
                        if v is not None:
                            setattr(permissions, k, v)

        if only_true:
            p = [(k, v) for k, v in permissions if v]
        elif only_false:
            p = [(k, v) for k, v in permissions if not v]
        else:
            p = permissions

        return f'Permissions of **{target}**```\n' + '\n'.join(f'{PERM_THERE if v else PERM_MISSING} | {k}' for k, v in p) + '```'