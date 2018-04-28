from objects.modulebase import ModuleBase
from objects.permissions import (
    PermissionEmbedLinks, PermissionAddReactions,
    PermissionReadMessageHistory, PermissionManageMessages
)

from utils.funcs import find_channel

from discord import Embed, Colour, NotFound, Forbidden

import asyncio


EMOJI_NUMBER_BASE = '{}⃣'

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <subject> <choice 1> <choice 2> [choices 3-9]'
    short_doc = 'Begin poll.'
    additional_doc = (
        'Subcommands:\n'
        '\t{prefix}{aliases} cancel - cancels poll\n\n'
        'Command flags:\n'
        '\t--timeout or -t <seconds> - set custom timeout, default is 30\n'
    )

    name = 'poll'
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
        self.polls = {}

    async def on_call(self, msg, args, **flags):
        if args[1].lower() == 'cancel':
            author, poll = self.polls.get(msg.channel.id, (None, None))
            if not poll:
                return '{warning} No active poll in channel'

            if msg.author != author:
                manage_messages_perm = PermissionManageMessages()
                if not manage_messages_perm.check(msg.channel, msg.author):
                    raise manage_messages_perm

            del self.polls[poll.channel.id]
            return await self.bot.edit_message(poll, content='[CANCELLED]')
        elif len(args) < 4:
            return await self.on_not_enough_arguments(msg)

        if msg.channel.id in self.polls:
            return '{warning} Channel already have active poll'

        timeout = flags.get('timeout', '30')
        if not timeout.isdigit():
            return '{error} Timeout is not a correct number'

        timeout = int(timeout)
        if not 10 <= timeout <= 3600:
            return '{error} Timeout should be between **10** and **3600** seconds'

        if len(args) > 11:
            return '{error} Can\'t start poll with more than 9 items'

        subject = f'Poll: {args[1]}'
        if len(subject) > 256:
            return '{error} Subject name can\'t be longer than 250 characters'

        choices = args.args[2:]
        emojis = [EMOJI_NUMBER_BASE.format(i + 1) for i in range(len(choices))]

        e = Embed(colour=Colour.gold(), title=subject)
        e.description = '\n'.join(f'{emojis[i]}: {c}' for i, c in enumerate(choices))
        e.set_author(name=msg.author.name, icon_url=msg.author.avatar_url)
        e.set_footer(text=f'React with {emojis[0]} - {emojis[-1]} to vote, {timeout} seconds')

        poll = await self.send(msg, embed=e)
        self.polls[poll.channel.id] = (msg.author, poll)

        try:
            for e in emojis:
                await poll.add_reaction(e)
        except NotFound:
            del self.polls[poll.channel.id]
            return

        await asyncio.sleep(timeout)

        if msg.channel.id not in self.polls:  # poll cancelled
            return

        del self.polls[poll.channel.id]

        try:
            poll = await msg.channel.get_message(poll.id)
            await poll.edit(content='[FINISHED]')
        except NotFound:
            return

        scores = [0] * len(choices)
        for r in poll.reactions:
            try:
                index = emojis.index(str(r.emoji))
            except ValueError:
                continue
            else:
                scores[index] = r.count - 1

        max_score = max(scores)

        e = Embed(colour=Colour.gold(), title=subject)
        e.description = 'Results\n'
        for s, c in sorted(zip(scores, choices), key=lambda x: (-x[0], x[1])):
            e.description += f'{c}: {s}'
            e.description += ' (WINNER)\n' if s == max_score else '\n'

        await self.send(msg, embed=e)