# coding:utf8

import os
import sys

from utils import ACCESS_LEVEL_NAMES, AUTHOR_ID


class CommandManager(object):
    
    def __init__(self, bot):
        self.bot = bot
        self.commands = {}

    def load_commands(self, command_paths=['commands']):
    	commands_found = []

    	for path, dirs, files in os.walk(command_paths[0]):
    		for f in files:
    			if f.startswith('command_') and f.endswith('.py'):
    				commands_found.append(path + os.sep + f)

    	for command_path in commands_found:
    		command_name = command_path[command_path.rfind(os.sep) + 9:-3]
    		self.commands[command_name] = self.load_command(command_path)
    		self.commands[command_name].on_load()

    def load_command(self, command_path):
    	return getattr(__import__(command_path.replace(os.sep, '.')[:-3], fromlist=['Command']), 'Command')(self.bot)

    async def check_commands(self, message):
    	for name in self.commands.keys():
    		if not await self.commands[name].check_message(message):
    			continue

    		if not await self.check_argument_count(name, message):
    			return '❗ Not enough arguments to call ' + name

    		if not await self.check_permissions(name, message):
    			return '⛔ Access demied. Minimum access level to use command is `' + ACCESS_LEVEL_NAMES[self.commands[name].protection] + '`'

    		return await self.commands[name].on_call(message)

    async def check_argument_count(self, command_name, message):
    	return len(message.content.split()) - 1 >= self.commands[command_name].arguments_required

    async def check_permissions(self, command_name, message):
    	return await self.get_user_access_level(message) >= self.commands[command_name].protection

    async def get_user_access_level(self, message):
    	if message.author.id == AUTHOR_ID:
    		return 3
    	else:
    		return 0
