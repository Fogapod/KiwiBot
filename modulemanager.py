# coding:utf8

import os
import sys
import traceback

from importlib import reload

from utils.constants import ACCESS_LEVEL_NAMES
from utils.checks import get_user_access_level


class ModuleManager(object):
    
    def __init__(self, bot):
        self.bot = bot
        self.modules = {}
        self._modules = {}

    async def load_modules(self, module_dirs=['modules']):
        modules_found = []

        for path, dirs, files in os.walk(module_dirs[0]):
            for f in files:
                if f.startswith('module_') and f.endswith('.py'):
                    modules_found.append(path + os.sep + f)

        for module_path in modules_found:
            module_name = module_path[module_path.rfind(os.sep) + 8:-3]
            try:
                await self.load_module(module_path)
            except Exception:
                await self.unload_module(module_name)
                raise ModuleLoadingException(module_name, module_path)

    async def load_module(self, module_path):
        try:
            imported = __import__(
                module_path.replace(os.sep, '.')[:-3], fromlist=['Module'])
            module = getattr(imported, 'Module')(self.bot)
            await module.on_load()
        except Exception:
            raise ModuleLoadingException(module_path[module_path.rfind(os.sep) + 8:-3], module_path)
        else:
            self.modules[module.name] = module
            self._modules[module.name] = imported

    async def reload_modules(self):
        for name in self._modules:
            await self.reload_module(name)

    async def reload_module(self, name):
        reloaded = reload(self._modules[name])
        module = getattr(reloaded, 'Module')(self.bot)

        await module.on_load()

        self._modules[name] = reloaded
        self.modules[name] = module

    async def unload_modules(self):
        pass

    async def unload_module(self, name):
        pass

    async def check_modules(self, message):
        args = message.content.split()

        for module in self.modules.values():
            if not await module.check_message(message, *args):
                continue

            if not self.check_argument_count(module, len(args)):
                return module.not_enough_arguments_text

            if not await self.check_permissions(module, message):
                return module.permission_denied_text

            return await module.on_call(message, *args)

    def check_argument_count(self, module, argc):
    	return argc - 1 >= module.arguments_required

    async def check_permissions(self, module, message):
    	return await get_user_access_level(message) >= module.protection


class ModuleLoadingException(Exception):
    def __init__(self, module_name, module_path):
        self.module_name = module_name
        self.module_path = module_path
        super(ModuleLoadingException, self).__init__(self)

    def __str__(self):
        return 'Failed to load module {0} ({1})'.format(self.module_name, self.module_path)
