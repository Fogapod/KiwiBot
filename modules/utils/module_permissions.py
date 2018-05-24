from objects.modulebase import ModuleBase

from utils.funcs import find_role, find_user, find_channel

from discord import Permissions, TextChannel, VoiceChannel


PERM_MISSING = '❌'
PERM_THERE   = '✅'

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [member|role]'
    short_doc = 'Show list of member or role permissions'
    long_doc = (
        'Available flags:\n'
        '\t[--channel|-c]: channel to check permissions in\n'
        '\t-t:             show permissions set to true only\n'
        '\t-f:             show permissions set to false only\n'
        '\t[--global|-g]:  show guild permissions\n'
        '\t[--value|-v]:   use custom permission value'
    )

    name = 'permissions'
    aliases = (name, 'perms')
    category = 'Discord'
    flags = {
        'value': {
            'alias': 'v',
            'bool': False
        },
        'channel': {
            'alias': 'c',
            'bool': False
        },
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

    async def on_call(self, ctx, args, **flags):
        value = flags.pop('value', None)

        if value:
            if flags:
                return '{error} value flag conflict with all other flags'

            if not value.isdigit():
                return '{error} value is not integer'

            permissions = Permissions(permissions=int(value))
        else:
            permissions = None

        channel_flag = flags.pop('channel', None)
        if channel_flag is None:
            channel = ctx.channel
        else:
            channel = await find_channel(channel_flag, ctx.guild)
            if channel is None:
                return '{warning} Channel not found'

        only_true  = flags.pop('t', False)
        only_false = flags.pop('f', False)
        use_global = flags.pop('global', False)

        if only_true and only_false:
            return '{error} t and f flags conflict'

        if permissions is not None:
            target = value
        elif len(args) == 1:
            if use_global:
                permissions = ctx.author.guild_permissions
            else:
                permissions = channel.permissions_for(ctx.author)
            target = str(ctx.author)
        else:
            role = await find_role(args[1:], ctx.guild)
            if role is not None:
                permissions = role.permissions
                target = str(role)

                if use_global:
                    if permissions.administrator:
                        permissions = Permissions.all()
                elif permissions.administrator:
                    if isinstance(channel, VoiceChannel):
                        permissions = Permissions(
                            Permissions.all().value & ~Permissions.text().value)
                    elif isinstance(channel, TextChannel):
                        permissions = Permissions(
                            Permissions.all().value & ~Permissions.voice().value)
                    else:
                        permissions = Permissions(
                            Permissions.all().value
                            & ~Permissions.text().value
                            & ~Permissions.voice().value
                        )
                else:
                    for k, v in channel.overwrites_for(role):
                        if v is not None:
                            setattr(permissions, k, v)
            else:
                member = await find_user(args[1:], ctx.message, strict_guild=True)
                if member is None:
                    return '{warning} Role or member not found'

                if use_global:
                    permissions = member.guild_permissions
                else:
                    permissions = channel.permissions_for(member)
                target = str(member)

        if only_true:
            p = [(k, v) for k, v in permissions if v]
        elif only_false:
            p = [(k, v) for k, v in permissions if not v]
        else:
            p = permissions

        return f'Permissions of **{target}** in **{channel.mention if not use_global else ctx.guild}**```\n' + '\n'.join(f'{PERM_THERE if v else PERM_MISSING} | {k}' for k, v in p) + '```'