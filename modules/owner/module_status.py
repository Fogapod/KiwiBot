from objects.modulebase import ModuleBase
from objects.permissions import (
    PermissionBotOwner, PermissionAddReactions, PermissionReadMessageHistory)
from objects.paginators import Paginator, SelectionPaginator

from discord import Activity, Status

import asyncio


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <subcommand> [args...]'
    short_doc = 'Bot presence utils'
    long_doc = (
        'Subcommands:\n'
        '\tplaying - set playing activity\n'
        '\tstreaming - set streaming activity\n'
        '\tlistening - set listening activity\n'
        '\twatching - set watching activity\n'
        '\tlist - show all activities\n'
        '\tremove - remove activity from list\n\n'
        'Flags:\n'
        '\t[--status|-s] <name>:    select status (online, dnd, etc)\n'
        '\t[--interval|-i] <time>:  change activity change interval'
    )

    name = 'status'
    aliases = (name, 'presence', 'activity')
    category = 'Owner'
    
    bot_perms = (PermissionAddReactions(), PermissionReadMessageHistory())
    user_perms = (PermissionBotOwner(), )
    min_args = 1
    flags = {
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

    async def on_missing_permissions(self, ctx, *missing):
        return 'not dogsong or notsosuper'

    async def on_load(self, from_reload):
        return await self._change_precense(
            0,
            'change da world... my final message Goodb ye',
            'online'
        )

        self.interval = int(
            await self.bot.redis.get('activity_interval', default=60))
        self._task = asyncio.ensure_future(
            self.update_presence_task(), loop=self.bot.loop)

    async def on_unload(self):
        pass  # self._task.cancel()

    async def on_call(self, ctx, args, **flags):
        interval = flags.get('interval', None)
        if interval is not None:
            if not interval.isdigit():
                return await ctx.warn('Interval is not integer')

            interval = int(interval)
            if interval < 20:
                return await ctx.warn('Minimum allowed interval is 20 seconds')

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

            return await p.run(ctx)

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

            await p.run(ctx, len(lines))
            if p.choice is not None:
                await self.bot.redis.srem('activity', items[p.choice - 1])
                return f'Deleted activity `{items[p.choice - 1]}`'
            else:
                return
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
            return await self.on_doc_request(ctx)

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
                i += 1
            else:
                await self._change_precense(0, '', 'online')

            await asyncio.sleep(self.interval)

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
        name = name.replace('{help_cmd}', f'@{self.bot.user.name} help')

        return name
