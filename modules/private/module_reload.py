from modules.modulebase import ModuleBase


class Module(ModuleBase):
    """{prefix}{keywords} <target>
    
    Reload parts of the bot.

    Targets:
        bot: restarts bot
        modules: reloads all modules
        <command_name>: reload selected module

    {protection} or higher permission level required to use"""

    name = 'reload'
    keywords = (name, )
    arguments_required = 1
    protection = 2

    async def on_call(self, message, *args):
        target = args[1].lower()

        reload_message = await self.bot.send_message(
            message, 'Reloading `' + target + '` ...',
            response_to=message
        )

        if target == 'bot':
            await messge.add_reaction('✅')
            await self.bot.restart()

        elif target == 'modules':
            await self.bot.mm.reload_modules()

        elif target in self.bot.mm.modules:
            await self.bot.mm.reload_module(target)

        else:
            await self.bot.edit_message(
                reload_message, content='Unknown target `' + target + '`!')
            return

        await self.bot.edit_message(
            reload_message, content='Reloading `' + target + '` completed')