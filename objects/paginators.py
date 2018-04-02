from collections import OrderedDict
from asyncio import TimeoutError, wait
from concurrent.futures import FIRST_COMPLETED

import time

from discord.errors import Forbidden, NotFound


class PaginatorABC:

    def __init__(self, bot, looped=True, timeout=180):
        self.bot = bot

        self.looped = looped
        self.timeout = timeout

        self.index  = 0
        self._pages = []
        self.current_page = {}
        self.events = OrderedDict()
        self.target_users = []
        self.closed = False

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

    async def _reaction_add_callback(self, reaction, user):
        manage_messages_permission = \
            self.target_message.guild and self.target_message.channel.permissions_for(self.target_message.guild.me).manage_messages

        await self.events[str(reaction)](reaction, user)
        try:
            await self.target_message.remove_reaction(reaction, user)
        except Forbidden:
            pass
        except NotFound:
            self.closed = True

    async def _reaction_remove_callback(self, reaction, user):
        await self.events[str(reaction)](reaction, user)

    async def run(self, target_message, **kwargs):
        """
        Runs paginator session
        parameters:
            :target_message:
                message attach paginator to. Usually bot message
            :target_user: (default: None)
                user wait actions from. Can be User or Member object
            :target_users: (default: [])
                list of users wait actions from. Can be User or Member object list
            :events: (default: {})
                dict of events to wait as keys and their callbacks as values
                !events should be lambda functions creating actual coroutine on call!
                callbacks are coroutines recieving event result(s)
        """

        self.target_message = target_message

        target_user = kwargs.pop('target_user', None)
        target_users = kwargs.pop('target_users', [])
        events = kwargs.pop('events', {})

        if target_user is None and len(target_users) == 0:
            raise ValueError('No user objects passed')
        if target_user is not None:
            if len(target_users) != 0:
                raise ValueError('Use either target_user or target_users, not both')
            target_users.append(target_user)

        self.target_users = target_users
        await self.init_reactions(target_message)

        def check(reaction, user):
            return all((
                any(user == u for u in target_users),
                reaction.message.id == target_message.id,
                str(reaction.emoji) in self.events
             ))

        self.start_time = time.time()
        time_left = self.timeout

        manage_messages_permission = \
            target_message.guild and target_message.channel.permissions_for(target_message.guild.me).manage_messages

        while time_left >= 0 and not self.closed:
            reaction_add_event = self.bot.wait_for('reaction_add', check=check)
            _events = {l(): c for l, c in events.items()}
            _events[reaction_add_event] = self._reaction_add_callback

            if not manage_messages_permission:
                reaction_remove_event = self.bot.wait_for('reaction_remove', check=check)
                _events[reaction_remove_event] = self._reaction_remove_callback

            done, _ = await wait(
                _events.keys(), loop=self.bot.loop,
                timeout=time_left, return_when=FIRST_COMPLETED
            )
            if not done:
                # timeout
                break
            else:
                for task in done:
                    cb = _events[task._coro]
                    task_result = task.result()

                    if task_result is None:
                        continue

                    if type(task_result) is tuple:
                        results = task_result
                    else:
                        results = [task_result]

                    await cb(*results)

                self.start_time += 30
                time_left = self.timeout - (time.time() - self.start_time)

        await self.cleanup(target_message)

    async def cleanup(self, msg):
        try:
            await msg.clear_reactions()
        except (Forbidden, NotFound):
            pass
        self.closed = True


class Paginator(PaginatorABC):
    """
    Basic paginator class.
    Requires PermissionAddReactions to work
    """

    def __init__(self, *args,
        emoji_go_left='◀', emoji_go_right='▶',
        emoji_use_index='🔢', emoji_quit='⏹', **kwargs
        ):

        super().__init__(*args, **kwargs)

        self.events[emoji_go_left]   = self.on_go_left
        self.events[emoji_go_right]  = self.on_go_right
        self.events[emoji_use_index] = self.on_use_index
        self.events[emoji_quit]      = self.on_quit

    async def on_go_left(self, reaction, user):
        await self.bot.edit_message(self.target_message, **self.switch_to_prev_page())

    async def on_go_right(self, reaction, user):
        await self.bot.edit_message(self.target_message, **self.switch_to_next_page())

    async def on_use_index(self, reaction, user):
        index_request_message = None
        index_response_message = None

        def check(message):
            return all((
                message.author == user,
                message.channel == self.target_message.channel,
                message.content.isdigit()
            ))

        try:
            index_request_message = await self.target_message.channel.send('Please, send number of page you want to go')
            index_response_message = await self.bot.wait_for('message', timeout=10, check=check)
            index = int(index_response_message.content)
            await self.bot.edit_message(self.target_message, **self.switch_to_page(index - 1))
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

    async def on_quit(self, reaction, user):
        self.closed = True


class SelectionPaginator(Paginator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choice = None
        self.num_elements = 0

    async def _check_choice(self, msg):
        if await self.check_choice(msg):
            self.closed = True
            await self.on_valid_choice(msg)
        else:
            await self.on_invalid_choice(msg)

    async def check_choice(self, msg):
        return msg.content.isdigit() and 0 < int(msg.content) <= self.num_elements

    async def on_invalid_choice(self, msg):
        pass

    async def on_valid_choice(self, msg):
        self.choice = int(msg.content)
        await self.bot.delete_message(msg)

    async def run(self, target_message, num_elements, **kwargs):
        self.num_elements = num_elements

        def check(msg):
            return all((
                any(msg.author == u for u in self.target_users),
                msg.channel == target_message.channel
            ))

        message_event_lambda = lambda: self.bot.wait_for('message', check=check)

        await super().run(
            target_message,
            events={message_event_lambda: self._check_choice}, **kwargs
        )

        return self.choice