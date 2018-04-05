from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner, PermissionAddReactions
from objects.paginators import Paginator, SelectionPaginator

from discord import Activity, Status

import asyncio


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [subcommand] [args...]'
    short_doc = 'Bot presence utils'
    additional_doc = (
        'Suncommands:\n'
        '\tplaying   - set playing activity\n'
        '\tstreaming - set streaming activity\n'
        '\tlistening - set listening activity\n'
        '\twatching  - set watching activity\n'
        '\tlist      - show all activities\n'
        '\tremove    - remove activity from list\n\n'
        'Flags:\n'
        '\t[--status|-s] <name>   - select status (online, dnd, etc)\n'
        '\t[--interval|-i] <time> - change activity change interval'
    )

    name = 'status'
    aliases = (name, 'presence', 'activity')
    require_perms = (PermissionBotOwner, PermissionAddReactions)
    call_flags = {
        'status': {
            'alias': 's',
            'bool': False
        },
        'interval': {
            'alias': 'i',
            'bool': False
        }
    }
    hidden = True

    async def on_missing_user_permissions(self, msg, missing_permissions):
        return 'not dogsong or notsosuper'

    async def on_load(self, from_reload):
        if not from_reload:
            self.interval = int(
                await self.bot.redis.get('activity_interval', 60))
            self._task = asyncio.ensure_future(
                self.update_presence_task(), loop=self.bot.loop)

    async def on_unload(self):
        self._task.cancel()

    async def on_call(self, msg, args, **flags):
        interval = flags.get('interval', None)
        if interval is not None:
            if not interval.isdigit():
                return '{warning} Interval is not integer'

            interval = int(interval)
            if interval < 20:
                return '{warning} Minimum allowed interval is 20 seconds'

            self.interval = interval
            await self.bot.redis.set('activity_interval', interval)

            if len(args) == 1:
                return 'Interval updated'

        status = flags.get('status', 'online')

        subcommand = args[1].lower()

        if subcommand == 'list':
            items = await self.bot.redis.smembers('activity')
            if not items:
                return 'Nothing to show'

            lines = [f'{i + 1}) {p}' for i, p in enumerate(items)]
            lines_per_chunk = 4
            chunks = [lines[i:i + lines_per_chunk] for i in range(0, len(lines), lines_per_chunk)]

            p = Paginator(self.bot)
            for i, chunk in enumerate(chunks):
                p.add_page(content='List of activities:```\n' + '\n'.join(chunk) + '```')

            m = await self.send(msg, **p.current_page)
            await p.run(m, target_user=msg.author)
            return

        elif subcommand == 'remove':
            items = await self.bot.redis.smembers('activity')
            if not items:
                return 'Nothing to remove'
            if len(items) == 1:
                await self.bot.redis.srem('activity', items[0])
                await self._change_precense(0, '', 'online')
                return f'Deleted activity `{items[0]}`'

            lines = [f'{i + 1}) {p}' for i, p in enumerate(items)]
            lines_per_chunk = 4
            chunks = [lines[i:i + lines_per_chunk] for i in range(0, len(lines), lines_per_chunk)]

            p = SelectionPaginator(self.bot)
            for i, chunk in enumerate(chunks):
                p.add_page(content='Please, type index to remove```\n' + '\n'.join(chunk) + '```')

            m = await self.send(msg, **p.current_page)
            await p.run(m, len(lines), target_user=msg.author)
            if p.choice is not None:
                await self.bot.redis.srem('activity', items[p.choice - 1])
                return f'Deleted activity `{items[p.choice - 1]}`'

        elif subcommand == 'playing':
            a_type = 0
            a_name = args[2:]
        elif subcommand == 'streaming':
            a_type = 1
            a_name = args[2:]
        elif subcommand == 'listening':
            a_type = 2
            a_name = args[2:]
        elif subcommand == 'watching':
            a_type = 3
            a_name = args[2:]
        else:
            return await self.on_doc_request(msg)

        if a_name:
            await self.bot.redis.sadd('activity', f'{a_type}:{status}:{a_name}')
        await self._change_precense(a_type, a_name, status)

        return f'Status switched to `{a_name}`' if a_name else 'Status removed'

    async def update_presence_task(self):
        i = 0
        while True:
            if await self.bot.redis.exists('activity'):
                items = await self.bot.redis.smembers('activity')
                if i >= len(items):
                    i = 0
                activity = items[i]
                a_type, _, status_and_name = activity.partition(':')
                status, _, a_name = status_and_name.partition(':')

                await self._change_precense(a_type, a_name, status)
                await asyncio.sleep(self.interval)
                i += 1
            else:
                await self._change_precense(0, '', 'online')

    async def _change_precense(self, a_type, a_name, status):
        a = Activity(
            name=self.format_activity_name(a_name), type=int(a_type))
        try:
            await self.bot.change_presence(activity=a, status=status)
        except Exception:
            pass

    def format_activity_name(self, name):
        name = name.replace('{guilds}', str(len(self.bot.guilds)))
        name = name.replace('{users}',  str(len(self.bot.users)))
        name = name.replace('{emojis}', str(len(self.bot.emojis)))
        name = name.replace(
            '{help_cmd}', f'@{self.bot.user.name} ' +
            self.bot.mm.get_module('help').aliases[0]
        )
        return name