from modules.modulebase import ModuleBase

import traceback


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

    async def on_load(self):
        bot_reload_channel_id = self.bot.config.get('bot_reload_channel_id', 0)
        bot_reload_message_id = self.bot.config.get('bot_reload_message_id', 0)

        if bot_reload_channel_id and bot_reload_message_id:
            await self.bot.config.remove('bot_reload_channel_id')
            await self.bot.config.remove('bot_reload_message_id')

            channel = self.bot.get_channel(bot_reload_channel_id)
            message = await channel.get_message(bot_reload_message_id)

            await message.edit(content='Bot restarted')
        #raise Exception(1)

    async def on_call(self, msg, *args):
        target = args[1].lower()

        reload_message = await self.bot.send_message(
            msg, 'Reloading `' + target + '` ...',
            response_to=msg
        )

        if target == 'bot':
            await self.bot.config.put('bot_reload_channel_id', reload_message.channel.id)
            await self.bot.config.put('bot_reload_message_id', reload_message.id)
            self.bot.restart()

        elif target == 'modules':
            await self.bot.mm.reload_modules()

        elif target in self.bot.mm.modules:
            try:
                await self.bot.mm.reload_module(target)
            except Exception:
                await self.bot.edit_message(
                reload_message, content='Failed to reload module `' + target + '`. Exception:```py\n' + traceback.format_exc() + '```')
                return

        else:
            await self.bot.edit_message(
                reload_message, content='Unknown target `' + target + '`!')
            return

        await self.bot.edit_message(
            reload_message, content='Reloading `' + target + '` completed')