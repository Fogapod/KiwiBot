from collections import OrderedDict
from asyncio import TimeoutError, wait
from concurrent.futures import FIRST_COMPLETED

import time

from discord import TextChannel, DMChannel
from discord.errors import Forbidden, NotFound

from objects.context import Context


class PaginatorABC:

    def __init__(self, bot, looped=True, timeout=180, additional_time=20):
        self.bot = bot

        self.looped = looped
        self.timeout = timeout
        self.additional_time = additional_time

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

    async def init_reactions(self, force=False):
        if len(self._pages) <= 1 and not force:
            self.closed = True
            return

        try:
            for emoji in self.events.keys():
                await self.target_message.add_reaction(emoji)
        except Exception:
            pass

    async def _reaction_add_callback(self, reaction, user):
        await self.events[str(reaction)](reaction, user)
        try:
            await self.target_message.remove_reaction(reaction, user)
        except NotFound:
            self.closed = True
        except Exception:
            pass

    async def _reaction_remove_callback(self, reaction, user):
        await self.events[str(reaction)](reaction, user)

    async def run(self, target, **kwargs):
        """
        Runs paginator session
        parameters:
            :target:
                Message or Context object attach paginator to
            :target_user: (default: None or ctx author if ctx passed as target)
                user wait actions from. Can be User or Member object
            :target_users: (default: [])
                list of users wait actions from. Can be User or Member object list
            :force_run: (default: False)
                force run paginator even if missing pages
            :events: (default: {})
                dict of events to wait as keys and their callbacks as values
                !events should be lambda functions creating actual coroutine on call!
                callbacks are coroutines recieving event result(s)
        """

        if isinstance(target, Context):
            self.target_message = await target.send(**self.current_page)
            if self.target_message is None:
                return await self.cleanup()
            target_user = kwargs.pop('target_user', target.author)
        else:
            self.target_message = target
            target_user = kwargs.pop('target_user', None)

        target_users = kwargs.pop('target_users', [])
        force_run = kwargs.pop('force_run', False)
        events = kwargs.pop('events', {})

        if target_user is None and len(target_users) == 0:
            raise ValueError('No user objects passed')
        if target_user is not None:
            if len(target_users) != 0:
                raise ValueError('Use either target_user or target_users, not both')
            target_users.append(target_user)

        self.target_users = target_users

        def check(reaction, user):
            return all((
                any(user == u for u in target_users),
                reaction.message.id == self.target_message.id,
                str(reaction.emoji) in self.events
             ))

        self.start_time = time.time()
        time_left = self.timeout

        manage_messages_permission = \
            self.target_message.guild and self.target_message.channel.permissions_for(self.target_message.guild.me).manage_messages

        await self.init_reactions(force=force_run)

        while time_left >= 0 and not self.closed:
            reaction_add_event = self.bot.wait_for('reaction_add', check=check)
            _events = { l(): c for l, c in events.items() }
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

                self.start_time += self.additional_time
                time_left = self.timeout - (time.time() - self.start_time)

        await self.cleanup()

    async def cleanup(self):
        try:
            await self.target_message.clear_reactions()
        except Exception:
            pass

        self.closed = True

    def __len__(self):
        return len(self._pages)


class Paginator(PaginatorABC):
    """
    Basic paginator class.
    Requires PermissionAddReactions to work
    """

    def __init__(self, *args,
        emoji_go_left='◀', emoji_go_right='▶',
        emoji_use_index='🔢', **kwargs
        ):

        super().__init__(*args, **kwargs)

        self.events[emoji_go_left]   = self.on_go_left
        self.events[emoji_use_index] = self.on_use_index
        self.events[emoji_go_right]  = self.on_go_right

    async def on_go_left(self, reaction, user):
        if not self.looped and self.index == 0:
            return

        await self.bot.edit_message(
            self.target_message, **self.switch_to_prev_page())

    async def on_go_right(self, reaction, user):
        if not self.looped and self.index == len(self._pages) - 1:
            return

        await self.bot.edit_message(
            self.target_message, **self.switch_to_next_page())

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
            index = int(index_response_message.content) - 1
            if index != self.index:
                await self.bot.edit_message(self.target_message, **self.switch_to_page(index))
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

    async def run(self, target, num_elements, **kwargs):
        self.num_elements = num_elements

        def check(msg):
            return all((
                msg.author in (self.target_users),
                msg.channel == target.channel
            ))

        message_event_lambda = lambda: self.bot.wait_for('message', check=check)

        await super().run(
            target,
            events={ message_event_lambda: self._check_choice }, **kwargs
        )

        return self.choice


class UpdatingPaginator(PaginatorABC):

    def __init__(self, *args, emoji_update='🆕', emoji_go_back='🔙', timeout=60, additional_time=30, **kwargs):
        super().__init__(
            *args, timeout=timeout, additional_time=additional_time, **kwargs)

        self.events[emoji_update] = self.on_update

        self.emoji_go_back = emoji_go_back
        self.backup_pages = []

        self.first_page_switch = True
        self.last_time_popped = False

    async def run(self, target, update_func, **kwargs):
        self.update_func = update_func
        self.update_args = kwargs.pop('update_args', ())
        self.update_kwargs = kwargs.pop('update_kwargs', {})

        self.add_page(**await self.get_fields())

        await super().run(target, force_run=True, **kwargs)

    async def on_update(self, reaction, user):
        fields = await self.get_fields()
        if not fields:
            return

        await self.bot.edit_message(self.target_message, **fields)

        if self.first_page_switch:
            self.first_page_switch = False

            self.events[self.emoji_go_back] = self.on_go_back
            await self.init_reactions(force=True)

        self.last_time_popped = False

    async def on_go_back(self, reaction, user):
        if not self.last_time_popped:
            self.backup_pages.pop()

        if len(self.backup_pages) > 1:
            fields = self.backup_pages.pop()
            await self.bot.edit_message(self.target_message, **fields)
        else:
            await self.bot.edit_message(
                self.target_message, **self.backup_pages[0])

        self.last_time_popped = True

    async def get_fields(self):
        try:
            fields = await self.update_func(
                self, *self.update_args, **self.update_kwargs)
            fields = {} if fields is None else fields
        except Exception:
            fields = {}

        self.backup_pages.append(fields)
        return fields