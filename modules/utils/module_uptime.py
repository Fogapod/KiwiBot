from modules.modulebase import ModuleBase

import time


class Module(ModuleBase):
    """{prefix}{keywords}
    
    Get bot uptime.

    {protection} or higher permission level required to use"""

    name = 'uptime'
    keywords = (name, 'up')
    protection = 0

    async def on_call(self, message, *args):
        delta = time.time() - self.bot.start_time

        minutes, seconds = divmod(delta,   60)
        hours,   minutes = divmod(minutes, 60)
        days,    hours   = divmod(hours,   24)
        months,  days    = divmod(days,    30)
        years,   months  = divmod(months,  12)

        response = 'Up for: **'
        response += '{0}y '.format(int(years)) if years else ''
        response += '{0}mon '.format(int(months)) if months else ''
        response += '{0}d '.format(int(days)) if days else ''
        response += '{0}m '.format(int(minutes)) if minutes else ''
        response += '{0}s**'.format(int(seconds))

        return response