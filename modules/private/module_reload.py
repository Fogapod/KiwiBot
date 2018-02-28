from modules.modulebase import ModuleBase

from utils.formatters import format_response

import traceback


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <target>'
    short_doc = 'Reload parts of the bot.'
    additional_doc = (
        'Targets:\n'
        '\tbot: restarts bot\n'
        '\tmodules: reloads all modules\n'
        '\t<command_alias>: reload selected module'
    )

    name = 'reload'
    aliases = (name, )
    arguments_required = 1
    protection = 2
    hidden = True

    async def on_load(self, from_reload):
        if not from_reload:
            return

        try:
            reload_channel_id = self.bot.config.get('reload_channel_id', 0)
            reload_message_id = self.bot.config.get('reload_message_id', 0)

            if reload_channel_id and reload_message_id:
                await self.bot.config.remove('reload_channel_id')
                await self.bot.config.remove('reload_message_id')

                channel = self.bot.get_channel(reload_channel_id)
                message = await channel.get_message(reload_message_id)

                await message.edit(content='Bot restarted')
        except Exception:
            import traceback
            self.bot.logger.info(self.name + ': Failed to call on_load:\n' + traceback.format_exc())

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

        else:
            module = self.bot.mm.get_module(target)
            if module is None:
                await self.bot.edit_message(
                    reload_message, content=f'Unknown target `{target}`!')
                return

            target = module.name

            try:
                await self.bot.mm.reload_module(target)
            except Exception:
                response = '{error} ' + f'Failed to reload module `{target}`. Exception:```py\n{traceback.format_exc()}```'
                response = await format_response(response, msg, self.bot)
                await self.bot.edit_message(
                    reload_message,
                    content=response
                )
                return

        await self.bot.edit_message(
            reload_message, content=f'Reloading `{target}` completed')