from objects.modulebase import ModuleBase

import time


class Module(ModuleBase):

    short_doc = 'Get bot uptime.'

    name = 'uptime'
    aliases = (name, 'up')

    async def on_load(self, from_reload):
        self.start_time = time.time()

    async def on_call(self, message, *args, **flags):
        delta = time.time() - self.start_time

        minutes, seconds = divmod(delta,   60)
        hours,   minutes = divmod(minutes, 60)
        days,    hours   = divmod(hours,   24)
        months,  days    = divmod(days,    30)
        years,   months  = divmod(months,  12)

        response = 'Up for: **'
        response += '{0}y '.format(int(years))    if years   else ''
        response += '{0}mon '.format(int(months)) if months  else ''
        response += '{0}d '.format(int(days))     if days    else ''
        response += '{0}h '.format(int(hours))    if hours   else ''
        response += '{0}m '.format(int(minutes))  if minutes else ''
        response += '{0}s**'.format(int(seconds))

        return response