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
    guild_only = True

    async def on_call(self, ctx, args, **flags):
        if len(args) == 1:
            channel = ctx.channel
        else:
            channel = await find_channel(
                args[1:], ctx.guild, global_id_search=True,
                include_voice=False, include_category=False
            )
            if channel is None:
                return await ctx.warn('Channel not found')

            author = channel.guild.get_member(ctx.author.id)
            if not author or not channel.permissions_for(author).read_messages:
                return await ctx.error('You don\'t have permission to read messages in that channel')
            if channel.is_nsfw() > ctx.channel.is_nsfw():
                return await ctx.warn('Trying to access nsfw channel from sfw channel')

        m = await ctx.send('Generating...')

        try:
            messages = await channel.history(
                limit=1000, oldest_first=True,
                before=ctx.message.edited_at or ctx.message.created_at
            ).flatten()
        except Exception:
            return await self.bot.edit_message(m, 'Failed to read message history')

        words = [i for s in [m.content.split(' ') for m in messages if m.content] for i in s]

        num_words = min((random.randint(5, 100), len(words)))
        if num_words < 2:
            return await self.bot.edit_message(
                m, 'Not enough words to generate text')
        
        pairs = [(words[i].lower(), words[i + 1]) for i in range(len(words) - 1)]

        word_dict = {}

        for word_1, word_2 in pairs:
            if word_1 in word_dict:
                word_dict[word_1].append(word_2)
            else:
                word_dict[word_1] = [word_2]

        chain = [random.choice(words)]

        for i in range(num_words):
            word = chain[-1]
            if word in word_dict:
                next_word = random.choice(word_dict[word])
            else:
                next_word = random.choice(random.choice(tuple(word_dict.values())))
            chain.append(next_word)

        most_frequent_word = max(word_dict, key=lambda x: len(word_dict[x] if x else []))

        e = Embed(colour=Colour.gold(), title='Markov Chain')
        e.add_field(name='Channel', value=channel.mention)
        e.add_field(name='Words analyzed', value=len(words))
        e.add_field(
            name='Most frequent word',
            value=f'**{most_frequent_word[:256]}**: used **{len(word_dict[most_frequent_word])}** times ({round(len(word_dict[most_frequent_word]) / len(words), 4)}%)'
        )
        e.description = trim_text(' '.join(chain), max_len=2048)
        e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

        await self.bot.delete_message(m)
        await ctx.send(embed=e)
