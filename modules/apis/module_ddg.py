from objects.modulebase import ModuleBase
from objects.permissions import (
    PermissionEmbedLinks, PermissionAddReactions, PermissionReadMessageHistory)
from objects.paginators import Paginator

from discord import Embed, Colour


API_URL = 'https://api.duckduckgo.com'

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <query>'
    short_doc = 'Web search using duckduckgo'

    name = 'ddg'
    aliases = (name, 'duckduckgo')
    bot_perms = (
        PermissionEmbedLinks(), PermissionAddReactions(),
        PermissionReadMessageHistory()
    )
    min_args = 1

    async def on_call(self, msg, args, **flags):
        params = {
            'q': args[1:],
            'o': 'json',
            'no_html': 1
        }

        async with self.bot.sess.get(API_URL, params=params) as r:
            if r.status != 200:
                return '{error} request failed: ' + str(r.status)
            r_json = await r.json(content_type='application/x-javascript')

        def make_embed(page):
            e = Embed(colour=Colour.gold(), title='DuckDuckGo')
            e.set_footer(
                text=f'Page {page}',
                icon_url='https://duckduckgo.com/favicon.png'
            )
            return e

        abstract_text = r_json['AbstractText']
        related = r_json['RelatedTopics']

        p = Paginator(self.bot)

        if abstract_text:
            e = make_embed(1)
            e.description = abstract_text
            e.set_image(url=r_json['Image'])
            p.add_page(embed=e)
        elif not related:
            return '{warning} Nothing found'

        topics = []
        for topic in related:
            if topic.get('Name'):
                for subtopic in topic['Topics']:
                    subtopic['Text'] = f'[{topic["Name"]}] {subtopic["Text"]}'
                    topics.append(subtopic)
            else:
                topics.append(topic)

        topics_per_page = 5
        chunks = [topics[i:i + topics_per_page] for i in range(0, len(topics), topics_per_page)]

        for i, group in enumerate(chunks):
            e = make_embed(len(p._pages) + 1)
            for topic in group:
                e.add_field(name=topic['Text'][:255], value=topic['FirstURL'])
            p.add_page(embed=e)

        m = await self.send(msg, **p.current_page)
        await p.run(m, target_user=msg.author)