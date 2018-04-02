from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

from discord import Activity


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [type] [text]'
    short_doc = 'Update bot status.'
    additional_doc = (
        'Activity types:\n'
        '\tplaying (default)\n'
        '\tstreaming\n'
        '\tlistening\n'
        '\twatching\n\n'
        '*Leave empty to remove status'
    )

    name = 'status'
    aliases = (name, 'presence', 'activity')
    require_perms = (PermissionBotOwner, )
    hidden = True

    async def on_missing_user_permissions(self, msg, missing_permissions):
        return 'not dogsong or notsosuper'

    async def on_load(self, from_reload):
        if not await self.bot.redis.exists('last_status', 'last_status_type'):
            return

        last_status = await self.bot.redis.get('last_status', default='')
        last_status_type = int(await self.bot.redis.get('last_status_type', default=0))

        presence = Activity(name=last_status, type=last_status_type)
        await self.bot.change_presence(activity=presence)

    async def on_call(self, msg, args, **flags):
        a_type = 0
        a_name = ''

        if len(args) == 1:
            presence = Activity(name='')
        else:
            subcommand = args[1].lower()
            a_name = args[2:]

            if subcommand == 'playing':
                pass
            elif subcommand == 'streaming':
                a_type = 1
            elif subcommand == 'listening':
                a_type = 2
            elif subcommand == 'watching':
                a_type = 3
            else:
                a_name = args[1:]

        presence = Activity(name=a_name, type=a_type)

        await self.bot.change_presence(activity=presence)
        await self.bot.redis.set('last_status', presence.name)
        await self.bot.redis.set('last_status_type', presence.type.value)

        return f'Status switched to `{presence.name}`' if presence.name else 'Status removed'