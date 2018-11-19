from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks, PermissionAttachFiles

import time
import asyncio
import aiohttp

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

TIMEOUT = 15
DEFAULT_WAIT_TIME = 2
MAX_WAIT_TIME = 10

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <url>'
    short_doc = 'Screenshot webpage'
    long_doc = (
        'Command flags:\n'
        '\t[--wait|-w] <seconds>: stay on page for given amount of seconds before making a screenshot'
    )

    name = 'screenshot'
    aliases = (name, 'ss')
    category = 'Actions'
    min_args = 1
    max_args = 1
    bot_perms = (PermissionEmbedLinks(), PermissionAttachFiles())
    ratelimit = (1, 13)
    flags = {
        'wait': {
            'alias': 'w',
            'bool': False
        }
    }

    async def on_load(self, from_reload):
        self.lock = asyncio.Lock()

    async def on_call(self, ctx, args, **flags):
        try:
            wait_time = int(flags.get('wait', DEFAULT_WAIT_TIME))
        except Exception:
            return await ctx.warn('Failed to parse wait time')

        if wait_time < 0:
            return await ctx.warn('Wait time should be above or equal to 0')

        if wait_time > MAX_WAIT_TIME:
            return await ctx.warn(f'Wait time should belower or equal to {MAX_WAIT_TIME}')

        m = await ctx.send('Taking screenshot...')

        url = args[1]
        if url.startswith('<') and url.endswith('>'):
            url = url[1:-1]
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        proxy = self.bot.get_proxy()

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
        except aiohttp.ClientConnectionError as e:
            return await self.bot.edit_message(
                m, f'Unknown connection error happened: {e}\nTry using http:// protocol')

        await self._ratelimiter.increase_time(wait_time, ctx)

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

        try:
            async with timeout(TIMEOUT + wait_time):
                session = await start_session(service, browser)
                await session.set_window_size(1920, 1080)

                await session.get(url)
                opened_url = await session.get_url()
                await asyncio.sleep(wait_time)
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
