from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks, PermissionAttachFiles

import time
import asyncio
import aiohttp
import random

from os import devnull
from async_timeout import timeout

from discord import Embed, Colour, File
from arsenic import start_session, stop_session, services, browsers
from arsenic.errors import UnknownArsenicError, UnknownError

import logging
import structlog


logger = logging.getLogger('arsenic')
logger.setLevel(logging.CRITICAL)

structlog.configure(logger_factory=lambda: logger)

TIMEOUT = 20

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <url>'
    short_doc = 'Screenshot webpage'

    name = 'screenshot'
    aliases = (name, 'ss')
    category = 'Actions'
    min_args = 1
    max_args = 1
    bot_perms = (PermissionEmbedLinks(), PermissionAttachFiles())
    ratelimit = (1, 15)

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
            async with self.bot.sess.head(url, timeout=TIMEOUT, proxy=proxy) as r:
                if (r.content_length or 0) > 100000000:
                    return await self.bot.edit_message(
                        m, 'Rejected to navigate, content is too long')
        except asyncio.TimeoutError:
            return await self.bot.edit_message(m, 'Connection timeout')
        except aiohttp.InvalidURL:
            return await self.bot.edit_message(m, 'Invalid url given')
        except aiohttp.ClientHttpProxyError:
            return await self.bot.edit_message(m, 'Host resolution error')
        except (aiohttp.ClientConnectorCertificateError, aiohttp.ClientConnectorSSLError):
            return await self.bot.edit_message(
                m, f'Can\'t establish secure connection to {url}\nTry using http:// protocol')

        await self.lock.acquire()
 
        service = service = services.Chromedriver(log_file=devnull)
        browser = browsers.Chrome(
            chromeOptions={
                'args': [
                    '--headless', '--disable-gpu', f'proxy-server={proxy}', 'lang=en',
                    '--limit-fps=1', '--disable-mojo-local-storage',
                    '--hide-scrollbars', '--ipc-connection-timeout=5'
                ]
            }
        )

        session = await start_session(service, browser)
        await session.set_window_size(1920, 1080)

        try:
            async with timeout(TIMEOUT + 2):
                await session.get(url)
                opened_url = await session.get_url()
                await asyncio.sleep(2)
                screenshot = await session.get_screenshot()
        except asyncio.TimeoutError:
            return await self.bot.edit_message(
                m, f'Screenshot timeout reached: **{TIMEOUT}** sec')
        except (UnknownArsenicError, UnknownError):
            return await self.bot.edit_message(
                m, 'Unknown browser error happened')
        finally:
            try:
                self.lock.release()
            except Exception:
                pass

            await stop_session(session)

        try:
            title = opened_url.split('/')[2]
        except IndexError:
            title = "Screenshot"

        e = Embed(title=title[:256], colour=Colour.gold(), url=url)
        e.set_image(url='attachment://screenshot.png')

        f = File(screenshot, filename='screenshot.png')
        e.set_footer(
                text=f'[{round(time.time() - (m.created_at or m.edited_at).timestamp(), 1)} sec] Note: above content is user-generated.',
            icon_url=ctx.author.avatar_url
        )

        await self.bot.delete_message(m)
        await ctx.send(embed=e, file=f)
