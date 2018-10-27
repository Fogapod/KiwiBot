from objects.modulebase import ModuleBase

from utils.funcs import create_subprocess_exec, execute_process

import re
import asyncio
import time


PROXY_TEST_URL = 'https://httpbin.org'
PROXY_TEST_TIMEOUT = 5

class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [url]'
    short_doc = 'Get bot response time / ping url'

    name = 'ping'
    aliases = (name, )
    category = 'Bot'

    async def on_call(self, ctx, args, **flags):
        ping_msg = await ctx.send('Pinging ...')

        if len(args) == 2:
            domain = args[1].lower()
            if domain == 'proxies':
                result = ''
                if not self.bot.proxies:
                    return await ctx.info('I don\'t have any proxies to ping')

                tasks = []
                result = ''
                async def ping_task(url, name):
                    nonlocal result
                    begin = time.time()
                    try:
                        r = await self.bot.sess.head(
                                PROXY_TEST_URL, proxy=url, timeout=PROXY_TEST_TIMEOUT)
                    except Exception as e:
                        response_time = '-'
                        comment = f'Ping {PROXY_TEST_URL}: {e.__class__.__name__}'
                    else:
                        response_time = str(round((time.time() - begin) * 1000))
                        if len(response_time) > 4:
                            response_time = "999+"

                        response_time += 'ms'

                        if r.status == 200:
                            comment = 'ok'
                        else:
                            comment = f'Error pinging {PROXY_TEST_URL}: {r.status}'

                    result += f'{name:<20} | {response_time:<6} | {comment}\n'

                for url, name in self.bot.proxies.items():
                    tasks.append(ping_task(url, name))

                await asyncio.gather(*tasks)

                header = f'{"NAME":<20} | {"TIME":<6} | COMMENT\n'
                header += f'{"-" * 21}+{"-" * 8}+{"-" * 21}\n'

                return await self.bot.edit_message(ping_msg, f'```\n{header}{result}```')

            if domain.startswith('<') and domain.endswith('>'):
                domain = domain[1:-1]
            if re.fullmatch('https?://.+', domain):
                domain = re.sub('^https?://|/$', '', domain)
            try:
                domain = domain.encode('idna')
            except UnicodeError:
                pass
            else:
                program = ['ping', '-c', '4', domain]
                process, pid = await create_subprocess_exec(*program)
                stdout, stderr = await execute_process(process)

                if process.returncode in (0, 1):  # (successful ping, 100% package loss)
                    return await self.bot.edit_message(
                        ping_msg, f'```\n{stdout.decode() or stderr.decode()}```')

        msg_timestamp = ctx.message.edited_at or ctx.message.created_at
        delta = round((ping_msg.created_at.timestamp() - msg_timestamp.timestamp()) * 1000)

        result = f'Pong, it took `{int(delta)}ms`'

        target = args[1:]
        result += f' to ping `{target}`' if target else ' to respond'

        await self.bot.edit_message(ping_msg, result)
