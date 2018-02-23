import re
import asyncio

from utils.logger import Logger


logger = Logger.get_logger()

async def create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    ):
    process = await asyncio.create_subprocess_exec(
        *args, stdout=stdout, stderr=stderr
    )
    return process, process.pid


async def create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    ):
    process = await asyncio.create_subprocess_shell(
        command, stdout=stdout, stderr=stderr
    )
    return process, process.pid


async def execute_process(process, code):
    logger.info('beg task:', str(code), '(pid = ' + str(process.pid) + ')')
    stdout, stderr = await process.communicate()
    logger.info('fin task:', str(code), '(pid = ' + str(process.pid) + ')')

    return stdout, stderr


async def find_user_in_guild(pattern, guild, bot):
    found = []
    for member in guild.members:
        if re.search(pattern, member.display_name, re.I) is None:
            if re.search(pattern, member.name + '#' + member.discriminator, re.I) is None:
                continue

        found.append(member)
    found.sort(key=lambda m: m.status.name == 'online', reverse=True)

    return found[0] if found else None


def get_string_after_entry(entry, string, strip=True):
    substring = string[string.index(entry) + len(entry):]
    return substring.lstrip() if strip else substring