# coding:utf8

import os
import sys
import traceback

from importlib import reload

from utils.constants import ACCESS_LEVEL_NAMES


class ModuleManager:
    
    def __init__(self, bot):
        self.bot = bot
        self.modules = {}
        self._modules = {}

    async def load_modules(self, module_dirs=['modules'], strict_mode=True):
        modules_found = []

        for path, dirs, files in os.walk(module_dirs[0]):
            for f in files:
                if f.startswith('module_') and f.endswith('.py'):
                    modules_found.append(path + os.sep + f)

        self.bot.logger.trace('Found ' + str(len(modules_found)) + ' modules')
        for module_path in modules_found:
            module_name = module_path[module_path.rfind(os.sep) + 8:-3]
            try:
                module = await self.load_module(module_path)
                await self.init_module(module)
            except Exception:
                self.bot.logger.info('Failed to load module ' + module_name)
                self.bot.logger.info(traceback.format_exc())

                if strict_mode:
                    raise
                    
        self.bot.logger.trace('Loaded ' + str(len(self.modules)) + ' modules')

    async def load_module(self, module_path):
        self.bot.logger.trace('Loading module from ' + module_path)
        imported = __import__(
            module_path.replace(os.sep, '.')[:-3], fromlist=['Module'])
        module = getattr(imported, 'Module')(self.bot)

        self.modules[module.name]  = module
        self._modules[module.name] = imported

        return module

    async def init_modules(self):
        for module in self.modules.values():
            await self.init_module(module)

    async def init_module(self, module):
        self.bot.logger.trace('Calling ' + module.name + ' on_load')
        await module.on_load()

    async def reload_modules(self):
        for module_name in self.modules:
            try:
                await self.reload_module(module_name)
            except Exception:
                self.bot.logger.info(
                    'Failed reloading module {0} ({1})'.format(
                        name, self._modules[name].__file__
                    )
                )
                self.bot.logger.debug(traceback.format_exc())
                raise

    async def reload_module(self, name):
        self.bot.logger.trace('Calling ' + name + ' on_unload')
        try:
            await self.modules[name].on_unload()
        except Exception:
            self.bot.logger.debug('Exception occured calling on_unload')
            self.bot.logger.debug(traceback.format_exc())

        self.bot.logger.trace('Reloading module ' + name)
        reloaded = reload(self._modules[name])
        module = getattr(reloaded, 'Module')(self.bot)

        await self.init_module(module)

        self._modules[name] = reloaded
        self.modules[name] = module

    async def unload_module(self, name):
        pass

    async def check_modules(self, message):
        args = message.content.split()

        for module in self.modules.values():
            if module.disabled:
                continue

            if not await module.check_message(message, *args):
                continue

            if not module.check_argument_count(len(args)):
                return module.not_enough_arguments_text

            if not await module.check_permissions(message):
                return module.permission_denied_text

            return await module.call_command(message, *args)