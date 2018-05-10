from objects.modulebase import ModuleBase

from constants import DEV_GUILD_ID


class Module(ModuleBase):

    usage_doc = ''
    short_doc = 'Member nick handlermyhandler'

    name = 'member-nicksmynicks'
    hidden = True

    async def on_load(self, from_reload):
        self.events = {
            'member_join':   self.on_member_join,
            'member_update': self.on_member_update
        }

    async def on_member_join(self, member):
        if member.guild.id == DEV_GUILD_ID:
            await self.set_nick(member)

    async def on_member_update(self, before, after):
        if after.guild.id == DEV_GUILD_ID:
            await self.set_nick(after)

    async def set_nick(self, member):
        left, _, right = member.display_name.partition('My')
        if left != right:
            n = member.display_name[:15]
            try:
                await member.edit(nick=f'{n}My{n}', reason='ReasonMyReason')
            except Exception:
                pass