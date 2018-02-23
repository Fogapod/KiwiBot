from modules.modulebase import ModuleBase

from utils.formatters import format_response

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
    hidden = True

    async def on_load(self, from_reload):
        if not from_reload:
            return

        reload_channel_id = self.bot.config.get('reload_channel_id', 0)
        reload_message_id = self.bot.config.get('reload_message_id', 0)

        if reload_channel_id and reload_message_id:
            await self.bot.config.remove('reload_channel_id')
            await self.bot.config.remove('reload_message_id')

            channel = self.bot.get_channel(reload_channel_id)
            message = await channel.get_message(reload_message_id)

            await message.edit(content='Bot restarted')

    async def on_call(self, msg, *args, **options):
        target = args[1].lower()

        reload_message = await self.bot.send_message(
            msg, 'Reloading `' + target + '` ...',
            response_to=msg
        )

        if target == 'bot':
            await self.bot.config.put('reload_channel_id', reload_message.channel.id)
            await self.bot.config.put('reload_message_id', reload_message.id)
            self.bot.restart()

        elif target == 'modules':
            try:
                await self.bot.mm.reload_modules()
            except Exception:
                response = '{error} Failed to reload modules. Exception:```py\n' + traceback.format_exc() + '```'
                response = await format_response(response, msg, self.bot)
                await self.bot.edit_message(
                    reload_message,
                    content=response
                )
                return

            await self.bot.edit_message(
                reload_message, content='Reloaded {0} modules: [{1}]'.format(
                    len(self.bot.mm.modules),
                    ', '.join(self.bot.mm.modules.keys())
                )
            )
            return

        elif target in self.bot.mm.modules:
            try:
                await self.bot.mm.reload_module(target)
            except Exception:
                response = '{error} Failed to reload module `' + target + '`. Exception:```py\n' + traceback.format_exc() + '```'
                response = await format_response(response, msg, self.bot)
                await self.bot.edit_message(
                    reload_message,
                    content=response
                )
                return

        else:
            await self.bot.edit_message(
                reload_message, content='Unknown target `' + target + '`!')
            return

        await self.bot.edit_message(
            reload_message, content='Reloading `' + target + '` completed')