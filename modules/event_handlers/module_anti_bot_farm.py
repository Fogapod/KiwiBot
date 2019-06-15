from objects.modulebase import ModuleBase


MEMBER_TRESHOLD = 50
BOT_PERCENT_TRESHOLD = 0.7

class Module(ModuleBase):

    usage_doc = ''
    short_doc = 'Leaves bot farms on join'

    name = 'antibotfarm'
    aliases = (name, )
    hidden = True

    async def on_load(self, from_reload):
        self.events = {
            'guild_join':  self.on_guild_join
        }

    async def on_guild_join(self, guild):
        def check(g):
            return g.member_count > MEMBER_TRESHOLD and sum([1 for m in g.members if m.bot]) / g.member_count > BOT_PERCENT_TRESHOLD

        if not check(guild):
            return

        try:
            await guild.owner.send(
                f"Someone added me to your guild {guild.name}[{guild.id}] recently which appears to be a bot farm.\n"
                f"Unfortunantely I am not able to function there and have to leave.\n\n"
                f"If you think this was a mistake, please consider contacting bot author."
            )
        except Exception:
            pass

        await guild.leave()
