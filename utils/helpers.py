import regex as re
import datetime
import asyncio

import discord

from utils.logger import Logger


logger = Logger.get_logger()

MENTION_REGEX = re.compile('<@!?(\d{17,19})>')


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


async def find_user(pattern, msg, bot, strict_guild=False, max_count=1):
    user = None
    id_match = re.fullmatch('(?:<@!?(\d{17,19})>)|\d{17,19}', pattern)

    if id_match is not None:
        user_id = int(id_match.group(1) or id_match.group(0))
        if msg.guild is not None:
            user = msg.guild.get_member(user_id)
        elif not strict_guild:
            user = bot.get_user(user_id)

        if user is None and not strict_guild:
            try:
                user = await bot.get_user_info(user_id)
            except discord.NotFound:
                return None

    if user is not None:
        return user if max_count == 1 else [user]

    if msg.guild is None:
        return None

    found_in_guild = []

    try:
        regex_pattern = re.compile(pattern, re.I)
    except Exception:
        # invalid regex, trying to use 'in'
        for member in msg.guild.members:
            if pattern not in member.display_name:
                if pattern not in str(member):
                    continue

            found_in_guild.append(member)
    else:
        for member in msg.guild.members:
            if regex_pattern.search(member.display_name) is None:
                if regex_pattern.search(str(member)) is None:
                    continue

            found_in_guild.append(member)

    found_in_guild.sort(
        key=lambda m: (
            _get_last_user_message_timestamp(m.id, msg.channel.id, bot),
            m.status.name == 'online',
            m.joined_at
        ),
        reverse=True
    )

    if found_in_guild:
        return found_in_guild[0] if max_count == 1 else found_in_guild[:max_count]

    return None


async def replace_mentions(content, bot):
    mentions = MENTION_REGEX.findall(content)
    if mentions:
        for m in mentions:
            m = int(m)
            user = discord.utils.get(bot.users, id=m)
            if user is None:
                try:
                    user = await bot.get_user_info(m)
                except discord.NotFound:
                    return content

            content = re.sub(f'(<@!?{user.id}>)', f'@{user}', content)
    return content


def _get_last_user_message_timestamp(user_id, channel_id, bot):
    if channel_id in bot._last_messages:
        if user_id in bot._last_messages[channel_id]:
            return bot._last_messages[channel_id][user_id].edited_at or bot._last_messages[channel_id][user_id].created_at
    return datetime.datetime.fromtimestamp(0)


async def get_local_prefix(msg, bot):
    if msg.guild is not None:
        guild_prefix = bot._guild_prefixes.get(msg.guild.id)
        if guild_prefix is not None:
            return guild_prefix
    return bot._default_prefixes[0]


async def request_reaction_confirmation(msg, user, bot, emoji_accept='✅', emoji_cancel='❌', timeout=20):
    try:
        for emoji in (emoji_accept, emoji_cancel):
            await msg.add_reaction(emoji)
    except discord.NotFound:
        return False

    def check(reaction, member):
        return all((
            member == user,
            reaction.message.id == msg.id,
            str(reaction.emoji) in (emoji_accept, emoji_cancel)
         ))

    try:
        reaction, member = await bot.wait_for('reaction_add', timeout=timeout, check=check)
    except asyncio.TimeoutError:
        pass
    else:
        if str(reaction) == emoji_accept:
            try:
                await msg.clear_reactions()
            except Exception:
                pass

            return True
    try:
        await msg.clear_reactions()
    except Exception:
        pass

    return False