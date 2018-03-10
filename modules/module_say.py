from modules.modulebase import ModuleBase

from permissions import PermissionManageMessages


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <text>'
    short_doc = 'Let me say something for you, lazy human.'

    name = 'say'
    aliases = (name, 'sayd')
    required_args = 1
    required_perms = (PermissionManageMessages, )

    async def on_call(self, msg, *args, **flags):
        await msg.delete()
        return msg.content.partition(args[0])[2].lstrip()