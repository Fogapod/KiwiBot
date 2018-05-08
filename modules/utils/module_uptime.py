from objects.modulebase import ModuleBase

import time


class Module(ModuleBase):

    short_doc = 'Get bot running time'

    name = 'uptime'
    aliases = (name, 'up')

    async def on_load(self, from_reload):
        self.start_time = time.time()

    async def on_call(self, msg, args, **flags):
        online_delta = time.time() - self.start_time

        return (
            f'Running: **{self.delta_to_str(self.bot.uptime)}**\n'
            f'Online: **{self.delta_to_str(online_delta)}**'
        )

    def delta_to_str(self, delta):
        s = ''

        delta = round(delta)

        minutes, seconds = divmod(delta,   60)
        hours,   minutes = divmod(minutes, 60)
        days,    hours   = divmod(hours,   24)
        months,  days    = divmod(days,    30)
        years,   months  = divmod(months,  12)

        s += '{0}y '.format(years)    if years   else ''
        s += '{0}mon '.format(months) if months  else ''
        s += '{0}d '.format(days)     if days    else ''
        s += '{0}h '.format(hours)    if hours   else ''
        s += '{0}m '.format(minutes)  if minutes else ''
        s += '{0}s'.format(seconds)   if seconds else ''

        return s