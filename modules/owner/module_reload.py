from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner

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
    required_args = 1
    require_perms = (PermissionBotOwner(), )
    hidden = True

    async def on_load(self, from_reload):
        if from_reload:
            return

        data = await self.bot.redis.get('reload_data')
        if data is None:
            return

        await self.bot.redis.delete('reload_data')
        channel_id, message_id = data.split(':')

        try:
            await self.bot.http.edit_message(
                int(message_id), int(channel_id), content='Bot restarted')
        except Exception:
            pass

    async def on_call(self, msg, args, **flags):
        target = args[1].lower()

        reload_message = await self.send(
            msg, content='Reloading `' + target + '` ...'
        )

        if target == 'bot':
            await self.bot.redis.set(
                'reload_data', f'{reload_message.channel.id}:{reload_message.id}')
            self.bot.restart()

        if target == 'modules':
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