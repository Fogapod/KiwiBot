from collections import OrderedDict
from asyncio import TimeoutError

import time

from discord.errors import Forbidden, NotFound


class Paginator:
    """
    Basic paginator class.
    Requires PermissionAddReactions to work
    """

    def __init__(self, bot, *args, looped=True, timeout=60,
        emoji_go_left='◀', emoji_go_right='▶',
        emoji_use_index='🔢', emoji_quit='⏹', **kwargs
        ):

        super().__init__(*args, **kwargs)
        self.index  = 0
        self._pages = []
        self.current_page = {}
        self.closed = False

        self.bot = bot
        self.looped = looped
        self.timeout = timeout
        self.events = OrderedDict()
        self.events[emoji_go_left]   = self.on_go_left
        self.events[emoji_go_right]  = self.on_go_right
        self.events[emoji_use_index] = self.on_use_index
        self.events[emoji_quit]      = self.on_quit

    def add_page(self, **kwargs):
        page = kwargs
        self._pages.append(page)

        if len(self._pages) == 1:
            self.current_page = page

    def switch_to_next_page(self):
        if self.index == len(self._pages) - 1:
            if not self.looped:
                return self.current_page
            self.index = 0
        else:
            self.index += 1
        
        return self._pages[self.index]

    def switch_to_prev_page(self):
        if self.index == 0:
            if not self.looped:
                return self.current_page
            self.index = len(self._pages) - 1
        else:
            self.index -= 1
        
        return self._pages[self.index]

    def switch_to_page(self, index):
        if len(self._pages) > index and index >= 0:
            self.index = index
        else:
            self.index = 0
        self.current_page = self._pages[self.index]
        return self.current_page

    async def init_reactions(self, msg):
        for emoji in self.events.keys():
            await msg.add_reaction(emoji)

    async def on_go_left(self, msg, reaction, user):
        await self.bot.edit_message(msg, **self.switch_to_prev_page())

    async def on_go_right(self, msg, reaction, user):
        await self.bot.edit_message(msg, **self.switch_to_next_page())

    async def on_use_index(self, msg, reaction, user):
        index_request_message = None
        index_response_message = None

        def check(message):
            return all((
                message.author == user,
                message.channel == msg.channel,
                message.content.isdigit()
            ))

        try:
            index_request_message = await msg.channel.send('Please, send number of page you want to go')
            index_response_message = await self.bot.wait_for('message', timeout=10, check=check)
            index = int(index_response_message.content)
            await self.bot.edit_message(msg, **self.switch_to_page(index - 1))
        except TimeoutError:
            pass
        finally:
            if index_request_message is not None:
               await index_request_message.delete()
            if index_response_message is not None:
                try:
                    await index_response_message.delete()
                except Exception:
                    pass

    async def on_quit(self, msg, reaction, user):
        await self.cleanup(msg)

    async def cleanup(self, msg):
        try:
            await msg.clear_reactions()
        except (Forbidden, NotFound):
            pass
        self.closed = True

    async def run_paginator(self, target_message, target_user, callback=None):
        manage_messages_permission = target_message.guild and target_message.channel.permissions_for(target_message.guild.me).manage_messages
        await self.init_reactions(target_message)

        def check(reaction, user):
            return all((
                user == target_user,
                reaction.message.id == target_message.id,
                str(reaction.emoji) in self.events
             ))

        self.start_time = time.time()
        time_left = self.timeout

        reaction_event = 'reaction_add'

        while time_left >= 0 and not self.closed:
            try:
                reaction, user = await self.bot.wait_for(reaction_event, timeout=time_left, check=check)
            except TimeoutError:
                await self.cleanup(target_message)
                return

            if callback is not None:
                if (await callback(reaction, user)) is False:
                    continue
            
            await self.events[str(reaction)](target_message, reaction, user)
            if reaction_event == 'reaction_add':
                if manage_messages_permission:
                    try:
                        await target_message.remove_reaction(reaction, user)
                    except Forbidden:
                        manage_messages_permission = False
                        reaction_event = 'reaction_remove'
                    except NotFound:
                        break
                else:
                    reaction_event = 'reaction_remove'
            else:
                reaction_event = 'reaction_add'

            self.start_time += 10
            time_left = 180 - (time.time() - self.start_time)