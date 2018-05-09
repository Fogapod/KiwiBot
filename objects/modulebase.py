from discord import DMChannel

from utils.funcs import get_local_prefix


class ModuleBase:

    usage_doc = '{prefix}{aliases}'
    short_doc = 'Not documented'
    long_doc = ''

    name             = ''     # name of module, should be same as in file name
    aliases          = ()     # default check_message event would search for matches in this tuple
    category         = ''     # name of category include module in. Should not conflict with aliases
    bot_perms        = ()     # needed bot permissions
    user_perms       = ()     # needed user permissions
    min_args         = 0      # minimum number if arguments
    max_args         = -1     # maximum number of arguments. -1 if no limit
    flags            = {}     # flags are specified here
    guild_only       = False  # can only be used in guild
    nsfw             = False  # can only be used in nsfw channel
    hidden           = False  # would be hidden when possible
    disabled         = False  # won't be checked or called
    events           = {}     # (name: function) pairs of events module will handle

    def __init__(self, bot):
        self.bot = bot

        if type(self.bot_perms) is not tuple:
            self.required_perms = (self.bot_perms, )

        if type(self.user_perms) is not tuple:
            self.require_perms = (self.user_perms, )

        # format call_flags dict
        self._flags = {}

        for k, v in self.flags.items():
            alias = v.get('alias', None)
            bool  = v.get('bool', False)

            if alias is not None:
                self._flags[alias] = { 'alias': k }
            self._flags[k] = { 'alias': k, 'bool': bool }

    async def on_guild_check_failed(self, msg):
        return '{error} This command can only be used in guild'

    async def on_nsfw_permission_denied(self, msg):
        return '{error} You can use this command only in channel marked as nsfw'

    async def on_not_enough_arguments(self, msg):
        return await self.on_doc_request(msg)

    async def on_too_many_arguments(self, msg):
        return await self.on_doc_request(msg)

    async def on_missing_permissions(self, msg, *missing):
        user_missing, bot_missing = [], []

        for p in missing:
            (user_missing, bot_missing)[p.is_bot_missing].append(p)

        response = ''

        if bot_missing:
            response += (
                '{error} I\'m missing the following permission' + ('s' if len(bot_missing) > 1 else '') +
                ' to execute command: ' + '[' + ', '.join([f'`{p.name}`' for p in bot_missing]) + ']\n'
            )
        if user_missing:
            response += (
                '{error} You\'re missing the following permission' + ('s' if len(user_missing) > 1 else '') +
                ' to use command: ' + '[' + ', '.join([f'`{p.name}`' for p in user_missing]) + ']'
            )

        return response

    async def on_load(self, from_reload):
        pass

    async def check_message(self, msg, args):
        if not (args and args[0].lower() in self.aliases):
            return False
        return await self.on_check_message(msg, args)

    async def on_check_message(self, msg, args):
        if (msg.guild is not None) < self.guild_only:
            raise GuildOnly

        if getattr(msg.channel, 'is_nsfw', lambda: isinstance(msg.channel, DMChannel))() < self.nsfw:
            raise NSFWPermissionDenied

        args.parse_flags(known_flags=self._flags)

        if len(args) - 1 < self.min_args:
            raise NotEnoughArgs

        if self.max_args > 0 and len(args) - 1 > self.max_args:
            raise TooManyArgs

        missing_permissions = []
        for permission in self.bot_perms:
            if not permission.check(msg.channel, self.bot.user):
                missing_permissions.append(permission)

        for permission in self.user_perms:
            if not permission.check(msg.channel, msg.author):
                missing_permissions.append(permission)

        if missing_permissions:
            raise MissingPermissions(*missing_permissions)

        return True

    async def call_command(self, msg, args, **flags):
        return await self.on_call(msg, args, **flags)

    async def on_call(self, msg, args, **flags):
        pass

    async def on_doc_request(self, msg):
        help_text = ''
        help_text += f'{self.usage_doc}'     if self.usage_doc else ''
        help_text += f'\n\n{self.short_doc}' if self.short_doc else ''
        help_text += f'\n\n{self.long_doc}'  if self.long_doc else ''

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
            + self.name + '**: **' + e.__class__.__name__ + '**\n'
            + 'Please report this to bot owner\n'
            + '```\n' + '\n'.join(tb_text.split('\n')[-4:]) + '\n```'
        )

    async def on_unload(self):
        pass

    async def send(self, msg, content=None, *, channel=None, **kwargs):
        return await self.bot.send_message(channel or msg, content, response_to=msg, **kwargs)


class ModuleCallError(Exception):
    pass


class GuildOnly(ModuleCallError):
    pass


class NSFWPermissionDenied(ModuleCallError):
    pass


class NotEnoughArgs(ModuleCallError):
    pass


class TooManyArgs(ModuleCallError):
    pass


class MissingPermissions(ModuleCallError):
    def __init__(self, *missing):
        self.missing = missing