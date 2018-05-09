from objects.modulebase import ModuleBase
from objects.permissions import (
    PermissionEmbedLinks, PermissionAddReactions,
    PermissionReadMessageHistory, PermissionManageMessages
)

from utils.funcs import find_channel, timedelta_from_string

from discord import Embed, Colour, NotFound, Forbidden

import time
import asyncio

from datetime import timezone


REACTION_FOR = '✅'
REACTION_AGAINST = '❎'

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <subject>'
    short_doc = 'Begin vote procedure'
    long_doc = (
        'Subcommands:\n'
        '\t{prefix}{aliases} cancel - cancels vote\n\n'
        'Command flags:\n'
        '\t[--timeout|-t] <time>: set custom timeout, default is 60\n\n'
        'Time formatting examples:\n'
        '\t1hour or 1h or 60m or 3600s or 3600 will result in 1 hour'
    )

    name = 'vote'
    aliases = (name, )
    category = 'Actions'
    bot_perms = (
        PermissionEmbedLinks(), PermissionAddReactions(),
        PermissionReadMessageHistory()
    )
    required_args = 1
    flags = {
        'timeout': {
            'alias': 't',
            'bool': False
        }
    }
    guild_only = True

    async def on_load(self, from_reload):
        self.votes = {}

        for key in await self.bot.redis.keys('vote:*'):
            value = await self.bot.redis.get(key)
            channel_id = int(key[5:])
            author_id, vote_id, expires_at = [int(i) for i in value.split(':')[:3]]

            channel = self.bot.get_channel(channel_id)
            author = self.bot.get_user(author_id)
            try:
                vote = await channel.get_message(vote_id)
            except NotFound:
                vote = None

            if None in (channel, author, vote):
                await self.bot.redis.delete(key)
                return

            self.votes[vote.channel.id] = self.bot.loop.create_task(
                self.end_vote(expires_at, author, vote))

    async def on_unload(self):
        for task in self.votes.values():
            task.cancel()

    async def on_call(self, msg, args, **flags):
        if args[1].lower() == 'cancel':
            task = self.votes.get(msg.channel.id)
            if not task:
                return '{warning} No active vote in channel found'

            value = await self.bot.redis.get(f'vote:{msg.channel.id}')
            author_id, vote_id = [int(i) for i in value.split(':')[:2]]

            if msg.author.id != author_id:
                manage_messages_perm = PermissionManageMessages()
                if not manage_messages_perm.check(msg.channel, msg.author):
                    raise manage_messages_perm

            task.cancel()
            await self.bot.redis.delete(f'vote:{msg.channel.id}')
            del self.votes[msg.channel.id]

            try:
                vote = await msg.channel.get_message(vote_id)
            except NotFound:
                pass
            else:
                await self.bot.edit_message(vote, content='[CANCELLED]')

            return await self.send(msg, content=f'**{msg.author}** cancelled vote.')

        if msg.channel.id in self.votes:
            return '{warning} Channel already have active vote'

        try:
            wait_until = timedelta_from_string(flags.get('timeout', '60'))
        except:
            return '{error} Failed to convert time'

        expires_at = wait_until.replace(tzinfo=timezone.utc).timestamp() + 1

        if not 10 <= expires_at - time.time() <= 3600 * 24 * 7 + 60:
            return '{error} Timeout should be between **10** seconds and **1** week'

        subject = args[1:]

        e = Embed(colour=Colour.gold(), title='Vote', description=subject)
        e.set_author(name=msg.author.name, icon_url=msg.author.avatar_url)
        e.set_footer(
            text=f'React with {REACTION_FOR} or {REACTION_AGAINST} to vote')
        e.timestamp = wait_until

        try:
            vote = await self.bot.send_message(msg.channel, embed=e)
            for e in (REACTION_FOR, REACTION_AGAINST):
                await vote.add_reaction(e)
        except NotFound:
            return

        await self.bot.delete_message(msg)

        await self.bot.redis.set(
            f'vote:{vote.channel.id}',
            f'{msg.author.id}:{vote.id}:{int(expires_at)}:{subject}'
        )
        self.votes[vote.channel.id] = self.bot.loop.create_task(
            self.end_vote(expires_at, msg.author, vote))

    async def end_vote(self, expires_at, author, vote):
        await asyncio.sleep(expires_at - time.time())

        value = await self.bot.redis.get(f'vote:{vote.channel.id}')
        author_id, vote_id, expires_at, subject = value.split(':', 3)

        await self.bot.redis.delete(f'vote:{vote.channel.id}')
        del self.votes[vote.channel.id]

        try:
            vote = await vote.channel.get_message(vote.id)
            await vote.edit(content='[FINISHED]')
        except NotFound:
            return

        voted_for, voted_against = 0, 0
        for r in vote.reactions:
            if str(r.emoji) == REACTION_AGAINST:
                voted_against = r.count - 1
            elif str(r.emoji) == REACTION_FOR:
                voted_for = r.count - 1

        total_votes = voted_for + voted_against
        percent_for = round(
            voted_for / total_votes * 100 if voted_for else 0.0, 2)
        percent_against = round(
            voted_against / total_votes * 100 if voted_against else 0.0, 2)

        author = self.bot.get_user(int(author_id))

        e = Embed(colour=Colour.gold(), title='Vote results', description=subject)
        e.set_author(name=author.name, icon_url=author.avatar_url)
        e.add_field(
            name=f'{total_votes} votes',
            value=f'For: **{voted_for}** (**{percent_for}**%)\nAgainst: **{voted_against}** (**{percent_against}**%)'
        )

        await self.bot.send_message(vote.channel, embed=e)