from objects.modulebase import ModuleBase
from objects.permissions import (
    PermissionEmbedLinks, PermissionAddReactions,
    PermissionReadMessageHistory, PermissionManageMessages
)

from utils.funcs import timedelta_from_string

from discord import Embed, Colour, NotFound, Forbidden

import time
import asyncio

from datetime import timezone


EMOJI_NUMBER_BASE = '{}⃣'

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <subject> <choice 1> <choice 2> [choices 3-9]'
    short_doc = 'Begin poll'
    long_doc = (
        'Subcommands:\n'
        '\t{prefix}{aliases} cancel - cancels poll\n\n'
        'Command flags:\n'
        '\t[--timeout|-t] <time>: set custom timeout, default is 60\n\n'
        'Time formatting examples:\n'
        '\t1hour or 1h or 60m or 3600s or 3600 will result in 1 hour'
    )

    name = 'poll'
    aliases = (name, )
    category = 'Actions'
    bot_perms = (
        PermissionEmbedLinks(), PermissionAddReactions(),
        PermissionReadMessageHistory()
    )
    min_args = 1
    flags = {
        'timeout': {
            'alias': 't',
            'bool': False
        }
    }
    guild_only = True

    async def on_load(self, from_reload):
        self.polls = {}

        for key in await self.bot.redis.keys('poll:*'):
            value = await self.bot.redis.get(key)
            channel_id = int(key[5:])
            author_id, poll_id, expires_at = [int(i) for i in value.split(':')[:3]]

            channel = self.bot.get_channel(channel_id)
            author = self.bot.get_user(author_id)
            try:
                poll = await channel.fetch_message(poll_id)
            except NotFound:
                poll = None

            if None in (channel, author, poll):
                await self.bot.redis.delete(key)
                await self.bot.redis.delete(f'poll_choices:{poll.channel.id}')
                return

            self.polls[poll.channel.id] = self.bot.loop.create_task(
                self.end_poll(expires_at, author, poll))

    async def on_unload(self):
        for task in self.polls.values():
            task.cancel()

    async def on_call(self, ctx, args, **flags):
        if args[1].lower() == 'cancel':
            task = self.polls.get(ctx.channel.id)
            if not task:
                return await ctx.warn('No active poll in channel found')

            value = await self.bot.redis.get(f'poll:{ctx.channel.id}')
            author_id, poll_id = [int(i) for i in value.split(':')[:2]]

            if ctx.author.id != author_id:
                manage_messages_perm = PermissionManageMessages()
                if not manage_messages_perm.check(ctx.channel, ctx.author):
                    raise manage_messages_perm

            task.cancel()
            await self.bot.redis.delete(f'poll_choices:{ctx.channel.id}')
            await self.bot.redis.delete(f'poll:{ctx.channel.id}')
            del self.polls[ctx.channel.id]

            try:
                poll = await ctx.channel.fetch_message(poll_id)
            except NotFound:
                pass
            else:
                await self.bot.edit_message(poll, content='[CANCELLED]')

            return await ctx.send(f'**{ctx.author}** cancelled poll.')
        elif len(args) < 4:
            return await self.on_not_enough_arguments(ctx)

        if ctx.channel.id in self.polls:
            return await ctx.warn('Channel already has active poll')

        try:
            wait_until = timedelta_from_string(flags.get('timeout', '60'))
        except:
            return await ctx.warn('Failed to convert time')

        expires_at = wait_until.replace(tzinfo=timezone.utc).timestamp() + 1

        if not 10 <= expires_at - time.time() <= 3600 * 24 * 7 + 60:
            return await ctx.error('Timeout should be between **10** seconds and **1** week')

        if len(args) > 11:
            return await ctx.error('Can\'t start poll with more than 9 items')

        subject = f'Poll: {args[1]}'
        if len(subject) > 256:
            return await ctx.error('Subject name can\'t be longer than 250 characters')

        choices = args.args[2:]
        emojis = [EMOJI_NUMBER_BASE.format(i + 1) for i in range(len(choices))]

        e = Embed(colour=Colour.gold(), title=subject)
        e.description = '\n'.join(f'{emojis[i]}: {c}' for i, c in enumerate(choices))
        e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.set_footer(
            text=f'React with {emojis[0]} - {emojis[-1]} to vote')
        e.timestamp = wait_until

        try:
            poll = await ctx.send(embed=e, register=False)
            for e in emojis:
                await poll.add_reaction(e)
        except NotFound:
            return

        await self.bot.delete_message(ctx.message)

        await self.bot.redis.set(
            f'poll:{poll.channel.id}',
            f'{ctx.author.id}:{poll.id}:{int(expires_at)}:{subject}'
        )
        await self.bot.redis.rpush(f'poll_choices:{poll.channel.id}', *choices)
        self.polls[poll.channel.id] = self.bot.loop.create_task(
            self.end_poll(expires_at, ctx.author, poll))

    async def end_poll(self, expires_at, author, poll):
        await asyncio.sleep(expires_at - time.time())

        value = await self.bot.redis.get(f'poll:{poll.channel.id}')
        author_id, poll_id, expires_at, subject = value.split(':', 3)
        choices = await self.bot.redis.lrange(
            f'poll_choices:{poll.channel.id}', 0, 8)

        await self.bot.redis.delete(f'poll_choices:{poll.channel.id}')
        await self.bot.redis.delete(f'poll:{poll.channel.id}')
        del self.polls[poll.channel.id]

        try:
            poll = await poll.channel.fetch_message(poll.id)
            await poll.edit(content='[FINISHED]')
        except NotFound:
            return

        scores = [0] * len(choices)
        emojis = [EMOJI_NUMBER_BASE.format(i + 1) for i in range(len(choices))]

        for r in poll.reactions:
            try:
                index = emojis.index(str(r.emoji))
            except ValueError:
                continue
            else:
                scores[index] = r.count - 1

        max_score = max(scores)

        author = self.bot.get_user(int(author_id))

        e = Embed(colour=Colour.gold(), title=subject)
        e.set_author(name=author, icon_url=author.avatar_url)
        e.description = 'Results\n'
        for s, c in sorted(zip(scores, choices), key=lambda x: (-x[0], x[1])):
            e.description += f'{c}: {s}'
            e.description += ' (WINNER)\n' if s == max_score else '\n'

        await self.bot.send_message(poll.channel, embed=e)
