from utils.constants import ACCESS_LEVEL_NAMES
from utils.helpers import get_local_prefix
from utils.checks import get_user_access_level


class ModuleBase:

    usage_doc = '{prefix}{aliases}'
    short_doc = 'Not documented'
    additional_doc = ''
    permission_doc = '{protection} or higher permission level required to use'

    name = 'module'
    aliases = ()
    guild_only = False
    nsfw = False
    arguments_required = 0
    protection = 0
    hidden = False
    disabled = False

    def __init__(self, bot):
        self.bot = bot

    async def check_guild(self, msg):
        return (msg.guild is not None) >= self.guild_only

    async def check_nsfw_permission(self, msg):
        return getattr(msg.channel, 'nsfw', False) >= self.nsfw

    async def check_argument_count(self, argc, msg):
        return argc - 1 >= self.arguments_required

    async def check_permissions(self, msg):
        return await get_user_access_level(msg) >= self.protection

    async def on_guild_check_failed(self, msg):
        return '{error} This command can only be used in guild'

    async def on_nsfw_prmission_denied(self, msg):
        return '{error} You can use this command only in channel marked as nsfw'

    async def on_not_enough_arguments(self, msg):
        return '{error} Not enough arguments to call ' + self.name

    async def on_permission_denied(self, msg):
        return '{error} Access demied. Minimum access level to use command is `' + ACCESS_LEVEL_NAMES[self.protection] + '`'

    async def on_load(self, from_reload):
        pass

    async def check_message(self, msg, *args, **flags):
        if self.disabled:
            return False
        return await self.on_check_message(msg, *args, **flags)

    async def on_check_message(self, msg, *args, **flags):
        return args and args[0].lower() in self.aliases

    async def call_command(self, msg, *args, **flags):
        return await self.on_call(msg, *args, **flags)

    async def on_call(self, msg, *args, **flags):
        pass

    async def on_message_edit(self, before, after, *args, **flags):
        pass

    async def on_message_delete(self, msg, *args, **flags):
        pass

    async def on_doc_request(self, msg):
        help_text = ''
        help_text += f'{self.usage_doc}'          if self.usage_doc else ''
        help_text += f'\n\n{self.short_doc}'      if self.short_doc else ''
        help_text += f'\n\n{self.additional_doc}' if self.additional_doc else ''
        help_text += f'\n\n{self.permission_doc}' if self.permission_doc else ''

        help_text = help_text.strip()

        return await self._format_help(help_text, msg)

    async def _format_help(self, help_text, msg):
        help_text = help_text.replace('{prefix}', await get_local_prefix(msg, self.bot))

        if len(self.aliases) == 1:
            help_text = help_text.replace('{aliases}', self.aliases[0])
        else:
            help_text = help_text.replace('{aliases}', '[' + '|'.join(self.aliases) + ']')

        help_text = help_text.replace('{protection}', ACCESS_LEVEL_NAMES[self.protection])

        return f'```\n{help_text}\n```'

    async def on_error(self, tb_text, msg):
        return (
            '{error} Error appeared during execution '
            + self.name
            + '```\n' + '\n'.join(tb_text.split('\n')[-4:]) + '\n```'
        )

    async def on_unload(self):
        pass

    async def send(self, msg, **kwargs):
        return await self.bot.send_message(msg, '', response_to=msg, **kwargs)