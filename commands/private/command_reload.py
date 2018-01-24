from commands.commandbase import CommandBase


class Command(CommandBase):
    """{prefix}{keywords} <target>
    
    Reload parts of the bot.

    Targets:


    {protection} or higher permission level required to use"""

    name = 'reload'
    keywords = (name, )
    arguments_required = 1
    protection = 2

    async def on_call(self, message):
        args = message.content.strip().split()
        target = args[1].lower()

        reload_message = await self.bot.send_message(
            message.channel, 'Reloading `' + target + '` ...',
            response_to=message
        )

        if target == 'all':
            await self.bot.edit_message(reload_message, '[WIP]')
            return

        elif target == 'commands':
            self.bot.cm.reload_commands()

        elif target in self.bot.cm.commands.keys():
            self.bot.cm.reload_command(target)

        else:
            await self.bot.edit_message(
                reload_message, 'Unknown target `' + target + '`!')
            return

        await self.bot.edit_message(
            reload_message, 'Reloading `' + target + '` completed')