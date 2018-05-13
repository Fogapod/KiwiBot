from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <args*>'
    short_doc = 'Redis db access'

    name = 'redis'
    aliases = (name, 'r')
    category = 'Owner'
    min_args = 1
    user_perms = (PermissionBotOwner(), )
    hidden = True

    async def on_call(self, ctx, args, **flags):
        value = await self.bot.redis.execute(*args.args[1:])

        return f'Return value: {self.to_string(value)}'
    
    def to_string(self, value):
        if type(value) is list:
            return str([self.to_string(v) for v in value])
        elif type(value) is bytes:
            return value.decode()
        else:
            return str(value)