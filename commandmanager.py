# coding:utf8

import os
import sys

from importlib import reload

from utils.constants import ACCESS_LEVEL_NAMES
from utils.checks import get_user_access_level


class CommandManager(object):
    
    def __init__(self, bot):
        self.bot = bot
        self.commands = {}
        self._modules = {}

    def load_commands(self, command_dirs=['commands']):
    	commands_found = []

    	for path, dirs, files in os.walk(command_dirs[0]):
    		for f in files:
    			if f.startswith('command_') and f.endswith('.py'):
    				commands_found.append(path + os.sep + f)

    	for command_path in commands_found:
    		command_name = command_path[command_path.rfind(os.sep) + 9:-3]
    		self.commands[command_name], self._modules[command_name] = \
    			self.load_command(command_path)
    		self.commands[command_name].on_load()

    def load_command(self, command_path):
    	module = __import__(
    		command_path.replace(os.sep, '.')[:-3], fromlist=['Command'])
    	return getattr(module, 'Command')(self.bot), module

    def reload_commands(self):
    	for name in self._modules:
    		self.reload_command(name)

    def reload_command(self, name):
    	reloaded = reload(self._modules[name])
    	self._modules[name] = reloaded
    	self.commands[name] = getattr(reloaded, 'Command')(self.bot)

    async def check_commands(self, message):
    	for name in self.commands:
    		if not await self.commands[name].check_message(message):
    			continue

    		if not await self.check_argument_count(name, message):
    			return self.commands[name].not_enough_arguments_text

    		if not await self.check_permissions(name, message):
    			return self.commands[name].permission_denied_text

    		return await self.commands[name].on_call(message)

    async def check_argument_count(self, command_name, message):
    	return len(message.content.split()) - 1 >= self.commands[command_name].arguments_required

    async def check_permissions(self, command_name, message):
    	return await get_user_access_level(message) >= self.commands[command_name].protection
