import re
import asyncio

from discord import NotFound

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


async def find_user(pattern, bot, guild=None, strict_guild=False, return_all=False):
    user = None
    id_match = re.fullmatch('(?:<@!?(\d{17,19})>)|\d{17,19}', pattern)

    if id_match is not None:
        user_id = int(id_match.group(1) or id_match.group(0))
        if guild is not None:
            user = guild.get_member(user_id)
        elif not strict_guild:
            user = bot.get_user(user_id)

        if user is None and not strict_guild:
            try:
                user = await bot.get_user_info(user_id)
            except NotFound:
                return None

    if user is not None:
        return [user] if return_all else user

    if guild is None:
        return None

    found_in_guild = []
    for member in guild.members:
        if re.search(pattern, member.display_name, re.I) is None:
            if re.search(pattern, f'{member.name}#{member.discriminator}', re.I) is None:
                continue

        found_in_guild.append(member)

    found_in_guild.sort(
        key=lambda m: (
            m.status.name == 'online',
            m.joined_at
        ),
        reverse=True
    )

    if found_in_guild:
        return found_in_guild if return_all else found_in_guild[0]

    return None


def get_string_after_entry(entry, string, strip=True):
    substring = string[string.index(entry) + len(entry):]
    return substring.lstrip() if strip else substring


async def get_local_prefix(msg, bot):
    if msg.guild is not None:
        guild_prefix = bot._guild_prefixes.get(msg.guild.id)
        if guild_prefix is not None:
            return guild_prefix
    return bot._default_prefixes[0]