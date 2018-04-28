from objects.modulebase import ModuleBase
from objects.permissions import (
    PermissionEmbedLinks, PermissionAddReactions,
    PermissionReadMessageHistory, PermissionManageMessages
)

from utils.funcs import find_channel

from discord import Embed, Colour, NotFound, Forbidden

import asyncio


REACTION_FOR = '✅'
REACTION_AGAINST = '❎'

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <subject>'
    short_doc = 'Begin vote procedure.'
    additional_doc = (
        'Subcommands:\n'
        '\t{prefix}{aliases} cancel - cancels vote\n\n'
        'Command flags:\n'
        '\t--timeout or -t <seconds> - set custom timeout, default is 30'
    )

    name = 'vote'
    aliases = (name, )
    required_perms = (
        PermissionEmbedLinks(), PermissionAddReactions(),
        PermissionReadMessageHistory()
    )
    required_args = 1
    call_flags = {
        'timeout': {
            'alias': 't',
            'bool': False
        }
    }
    guild_only = True

    async def on_load(self, from_reload):
        self.votes = {}

    async def on_call(self, msg, args, **flags):
        if args[1].lower() == 'cancel':
            author, vote = self.votes.get(msg.channel.id, (None, None))
            if not vote:
                return '{warning} No active vote in channel'

            if msg.author != author:
                manage_messages_perm = PermissionManageMessages()
                if not manage_messages_perm.check(msg.channel, msg.author):
                    raise manage_messages_perm

            del self.votes[vote.channel.id]
            return await self.bot.edit_message(vote, content='[CANCELLED]')

        if msg.channel.id in self.votes:
            return '{warning} Channel already have active vote'

        timeout = flags.get('timeout', '30')
        if not timeout.isdigit():
            return '{error} Timeout is not a correct number'

        timeout = int(timeout)
        if not 10 <= timeout <= 3600:
            return '{error} Timeout should be between **10** and **3600** seconds'

        e = Embed(colour=Colour.gold(), title='Vote', description=args[1:])
        e.set_author(name=msg.author.name, icon_url=msg.author.avatar_url)
        e.set_footer(
            text=f'React with {REACTION_FOR} or {REACTION_AGAINST} to vote, {timeout} seconds')

        vote = await self.send(msg, embed=e)
        self.votes[vote.channel.id] = (msg.author, vote)

        try:
            for e in (REACTION_FOR, REACTION_AGAINST):
                await vote.add_reaction(e)
        except NotFound:
            del self.votes[vote.channel.id]
            return

        await asyncio.sleep(timeout)

        if msg.channel.id not in self.votes:  # vote cancelled
            return

        del self.votes[vote.channel.id]

        try:
            vote = await msg.channel.get_message(vote.id)
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
        percent_for = voted_for / total_votes * 100 if voted_for else 0.0
        percent_against = voted_against / total_votes * 100 if voted_against else 0.0

        e = Embed(colour=Colour.gold(), title='Vote results', description=args[1:])
        e.set_author(name=msg.author.name, icon_url=msg.author.avatar_url)
        e.add_field(
            name=f'{total_votes} votes',
            value=f'For: **{voted_for}** (**{percent_for}**%)\nAgainst: **{voted_against}** (**{percent_against}**%)'
        )

        await self.send(msg, embed=e)