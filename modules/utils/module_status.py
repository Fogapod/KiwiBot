from modules.modulebase import ModuleBase

from permissions import PermissionBotOwner

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

    async def on_call(self, msg, *args, **flags):
        status = ''

        if len(args) == 1:
            presence = Activity(name='')
        else:
            subcommand = args[1].lower()
            status = msg.content.partition(args[1])[2].lstrip()

            if subcommand == 'playing':
                presence = Activity(name=status)
            elif subcommand == 'streaming':
                presence = Activity(name=status, type=1)
            elif subcommand == 'listening':
                presence = Activity(name=status, type=2)
            elif subcommand == 'watching':
                presence = Activity(name=status, type=3)
            else:
                status = msg.content.partition(args[0])[2].lstrip()
                presence = Activity(name=status)

        await self.bot.change_presence(activity=presence)
        await self.bot.redis.set('last_status', status)
        await self.bot.redis.set('last_status_type', presence.type.value)

        return f'Status switched to `{presence.name}`' if presence.name else 'Status removed'