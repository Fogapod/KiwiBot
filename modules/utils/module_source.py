from objects.modulebase import ModuleBase


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases}'
    short_doc = 'Gives link to source code of bot'

    name = 'source'
    aliases = (name, 'github')
    category = 'Bot'

    async def on_call(self, ctx, args, **flags):
        # hardcoded url fix?
        return 'My source code can be found here:\nhttps://github.com/Fogapod/KiwiBot'