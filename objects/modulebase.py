from utils.funcs import get_local_prefix


class ModuleBase:

    usage_doc = '{prefix}{aliases}'
    short_doc = 'Not documented.'
    additional_doc = ''

    name             = ''     # name of module, should be same as in file name
    aliases          = ()     # default on_check_message event would search for matches in this tuple
    required_perms   = ()     # permissions required for bot
    require_perms    = ()     # permissions required from user
    required_args    = 0      # number if required arguments
    guild_only       = False  # can only be used in guild
    nsfw             = False  # can only be used in nsfw channel
    hidden           = False  # would be hidden when possible
    disabled         = False  # won't be checked or called

    def __init__(self, bot):
        self.bot = bot

        # init permission classes
        if type(self.required_perms) is not tuple:
            self.required_perms = (self.required_perms(bot), )
        else:
            self.required_perms = tuple(p(bot) for p in self.required_perms)

        if type(self.require_perms) is not tuple:
            self.require_perms = (self.require_perms(bot), )
        else:
            self.require_perms = tuple(p(bot) for p in self.require_perms)

    def check_guild(self, msg):
        return (msg.guild is not None) >= self.guild_only

    def check_nsfw_permission(self, msg):
        return getattr(msg.channel, 'nsfw', False) >= self.nsfw

    def check_argument_count(self, argc, msg):
        return argc - 1 >= self.required_args

    async def get_missing_bot_permissions(self, msg):
        missing = []
        for permission in self.required_perms:
            if not await permission.check(msg, bot=True):
                missing.append(permission)

        return missing

    async def get_missing_user_permissions(self, msg):
        missing = []
        for permission in self.require_perms:
            if not await permission.check(msg, bot=False):
                missing.append(permission)

        return missing

    async def on_guild_check_failed(self, msg):
        return '{error} This command can only be used in guild'

    async def on_nsfw_permission_denied(self, msg):
        return '{error} You can use this command only in channel marked as nsfw'

    async def on_not_enough_arguments(self, msg):
        return await self.on_doc_request(msg)

    async def on_missing_bot_permissions(self, msg, missing):
        return (
            '{error} I\'m missing the following permissions to execute commamd: '
            '[' + ', '.join([f'`{p.name}`' for p in missing]) + ']'
        )

    async def on_missing_user_permissions(self, msg, missing):
        return (
            '{error} Access demied.\n'
            'You\'re missing the following permissions to use this command: '
            '[' + ', '.join([f'`{p.name}`' for p in missing]) + ']'
        )

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

        help_text = help_text.strip()

        return await self._format_help(help_text, msg)

    async def _format_help(self, help_text, msg):
        help_text = help_text.replace('{prefix}', await get_local_prefix(msg, self.bot))

        if len(self.aliases) == 1:
            help_text = help_text.replace('{aliases}', self.aliases[0])
        else:
            help_text = help_text.replace('{aliases}', '[' + '|'.join(self.aliases) + ']')

        return f'```\n{help_text}\n```'

    async def on_error(self, e, tb_text, msg):
        return (
            '{error} Error appeared during execution **'
            + self.name + '**: **' + e.__class__.__name__ + '**'
            + '```\n' + '\n'.join(tb_text.split('\n')[-4:]) + '\n```'
        )

    async def on_unload(self):
        pass

    async def send(self, msg, **kwargs):
        return await self.bot.send_message(msg, response_to=msg, **kwargs)