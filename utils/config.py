import os
import json
import asyncio


class Config(object):

    def __init__(self, config_file, **options):
        self.name = config_file

        try:
            with open(self.name, 'r') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            self._config = {}

        self.loop = options.pop('loop', asyncio.get_event_loop())
        self.lock = asyncio.Lock()

    def _dump(self):
        temp = self.name + '.temp'

        with open(temp, 'w', encoding='utf-8') as tmp:
            json.dump(self._config.copy(), tmp, ensure_ascii=False)

        os.replace(temp, self.name)

    async def save(self):
        with await self.lock:
            await self.loop.run_in_executor(None, self._dump)

    def get(self, key, *args):
        return self._config.get(str(key), *args)

    async def put(self, key, value):
        self._config[str(key)] = value
        await self.save()

    async def remove(self, key):
        del self._config[str(key)]
        await self.save()

    def all(self):
        return self._config

    def __getattr__(self, attr):
        return self._config[attr]

    def __getitem__(self, item):
        return self._config[str(item)]

    def __contains__(self, item):
        return str(item) in self._config