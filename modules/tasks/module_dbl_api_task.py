from objects.modulebase import ModuleBase

from objects.logger import Logger

import asyncio


logger = Logger()

API_URL = 'https://discordbots.org/api/bots/{bot_id}/stats'


class Module(ModuleBase):

    usage_doc = ''
    short_doc = 'Sends server count to discord bot list.'

    name = 'dbl_api_task'
    hidden = True

    async def on_load(self, from_reload):
        self._task = None
        self.dbl_token = self.bot.config.get('dbl_token')

        if not self.dbl_token:
            return

        global API_URL
        API_URL = API_URL.format(bot_id=self.bot.user.id)
        self._task = asyncio.ensure_future(self.guild_size_task(), loop=self.bot.loop)

    async def on_unload(self):
        if self._task is not None:
            self._task.cancel()

    async def guild_size_task(self):
        headers = {'Authorization': self.dbl_token}

        while True:
            data = {
                'server_count': len(self.bot.guilds),
                'shard_count':  len(self.bot.shards)
            }

            logger.debug(f'Sending data to DBL: {data}')

            try:
                await self.bot.sess.post(API_URL, headers=headers, data=data)
            except Exception as e:
                logger.debug(f'Error sneding data: {e}')

            await asyncio.sleep(1800)