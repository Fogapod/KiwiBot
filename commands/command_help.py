from commands.commandbase import CommandBase

from utils import PREFIXES, ACCESS_LEVEL_NAMES

import random


class Command(CommandBase):
    """{prefix}{keywords} <command>
    
    Get information about command.
    {protection} or higher permission level required to use"""

    name = 'help'
    keywords = (name, )
    arguments_required = 1
    protection = 0

    async def on_call(self, message):
    	args = message.content.split()

    	command = None

    	for k, v in self.bot.cm.commands.items():
    		if args[1] in v.keywords:
    			command = v

    	if not command:
    		return 'Command `' + args[1] + '` not found'

    	help_text = await command.on_doc_request()

    	if help_text:
    		return help_text

    	return await self.fornmat_help(command.__doc__, command)

    async def fornmat_help(self, help_text, command):
    	help_text = help_text.replace('\n    ', '\n')
    	help_text = help_text.replace('{prefix}', random.choice(PREFIXES[:-1]))

    	if len(command.keywords) == 1:
    		help_text = help_text.replace('{keywords}', command.keywords[0])
    	else:
    		help_text = help_text.replace('{keywords}', '[' + '|'.join(command.keywords) + ']')

    	help_text = help_text.replace('{protection}', ACCESS_LEVEL_NAMES[command.protection])

    	return '```\n' + help_text + '```'