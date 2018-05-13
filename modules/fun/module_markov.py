from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from utils.funcs import find_channel
from utils.formatters import trim_text

import random

from discord import Embed, Colour


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [channel]'
    short_doc = 'Generate text using markov chain'

    name = 'markov'
    aliases = (name, 'markovchain')
    category = 'Actions'
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, ctx, args, **flags):
        if len(args) == 1:
            channel = ctx.channel
        else:
            channel = await find_channel(
                args[1:], ctx.guild, self.bot,
                include_voice=False, include_category=False
            )
            if channel is None:
                return '{warning} Channel not found'

            if not channel.permissions_for(ctx.author).read_messages:
                return '{error} You don\'t have permission to read messages in that channel'

        m = await ctx.send('Generating...')

        try:
            messages = await channel.history(
                limit=200, before=ctx.message.edited_at or ctx.message.created_at
            ).flatten()
        except Exception:
            return await self.bot.edit_message(m, 'Failed to read message history')

        words = [i for s in [m.content.split() for m in messages] for i in s]

        num_words = random.randint(20, 200)
        if len(words) < num_words:
            return await self.bot.edit_message(
                m, 'Not enough words to generate text')

        def make_pairs(words):
            for i in range(len(words) - 1):
                yield (words[i], words[i + 1])
        
        pairs = make_pairs(words)

        word_dict = {}

        for word_1, word_2 in pairs:
            if word_1 in word_dict:
                word_dict[word_1].append(word_2)
            else:
                word_dict[word_1] = [word_2]

        chain = [random.choice(words)]

        for i in range(num_words):
            chain.append(random.choice(word_dict[chain[-1]]))

        e = Embed(colour=Colour.gold(), title='Markov Chain')
        e.description = trim_text(' '.join(chain), max_len=2048)
        e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

        await self.bot.delete_message(m)
        await ctx.send(embed=e)