from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks, PermissionAttachFiles

import time
import asyncio
import random

from os import devnull

from discord import Embed, Colour, File
from arsenic import start_session, stop_session, services, browsers, get_session
from arsenic.errors import UnknownArsenicError

import logging
import structlog


logger = logging.getLogger('arsenic')
logger.setLevel(logging.CRITICAL)

structlog.configure(logger_factory=lambda: logger)


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <url>'
    short_doc = 'Screenshot webpage'

    name = 'screenshot'
    aliases = (name, 'ss')
    category = 'Actions'
    min_args = 1
    max_args = 1
    bot_perms = (PermissionEmbedLinks(), PermissionAttachFiles())
    ratelimit = (1, 5)

    async def on_load(self, from_reload):
        self.lock = asyncio.Lock()

    async def on_call(self, ctx, args, **flags):
        m = await ctx.send('Taking screenshot...')

        url = args[1]
        if url.startswith('<') and url.endswith('>'):
            url = url[1:-1]
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        proxy = random.choice(list(self.bot.proxies.keys()))

        try:
            async with self.bot.sess.head(url, timeout=15, proxy=proxy) as r:
                if r.status == 503:
                    return await self.bot.edit_message(m, 'Host resolving issue')

                if (r.content_length or 0) > 100000000:
                    return await self.bot.edit_message(
                        m, 'Rejected to navigate')
        except Exception:
            return await self.bot.edit_message(m, 'Connection timeout')

        await self.lock.acquire()
 
        try:
            service = service = services.Chromedriver(log_file=devnull)
            browser = browsers.Chrome(
                chromeOptions={
                    'args': [
                        '--headless', '--disable-gpu', f'proxy-server={proxy}', 'lang=en', '--limit-fps=1',
                        '--disable-mojo-local-storage', '--hide-scrollbars', '--ipc-connection-timeout=5',
                        # '--timeout=5000'
                        # timeout flag completely breakes browser for some reason
                    ]
                }
            )

            async with get_session(service, browser) as session:
                await session.set_window_size(1920, 1080)
                await session.get(url)
                opened_url = await session.get_url()
                await asyncio.sleep(2)
                screenshot = await session.get_screenshot()
        except UnknownArsenicError:
            return await self.bot.edit_message(
                m, 'Unknown exception happened')
        except Exception:
            return await self.bot.edit_message(
                m, 'Could not open page, please check url and try again')
        finally:
            try:
               self.lock.release()
            except Exception:
                pass

        try:
            title = opened_url.split('/')[2]
        except IndexError:
            title = "Screenshot"

        e = Embed(title=title[:256], colour=Colour.gold(), url=url)
        e.set_image(url='attachment://screenshot.png')

        f = File(screenshot, filename='screenshot.png')
        e.set_footer(
            text=f'Took {round(time.time() - (m.created_at or m.edited_at).timestamp(), 1)} seconds')

        await self.bot.delete_message(m)
        await ctx.send(embed=e, file=f)
