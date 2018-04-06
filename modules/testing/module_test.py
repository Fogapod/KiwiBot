from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [args ...]'
    short_doc = 'Module for tests.'

    name = 'test'
    aliases = (name, )
    require_perms = (PermissionBotOwner(), )
    hidden = True

    async def on_call(self, msg, args, **flags):
        return f'Input:```\n{msg.content}```Args:```\n{args}```Flags:```\n{flags}```'