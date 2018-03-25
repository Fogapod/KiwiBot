import re
import datetime
import asyncio

import discord

from objects.logger import Logger


logger = Logger.get_logger()

ID_EXPR = '\d{17,19}'

ID_REGEX = re.compile(ID_EXPR)
MENTION_REGEX = re.compile(f'<@!?({ID_EXPR})>')
MENTION_OR_ID_REGEX = re.compile(f'(?:<@!?({ID_EXPR})>)|{ID_EXPR}')
ROLE_OR_ID_REGEX = re.compile(f'(?:<@&({ID_EXPR})>)|{ID_EXPR}')


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
    id_match = MENTION_OR_ID_REGEX.fullmatch(pattern)

    if id_match is not None:
        user_id = int(id_match.group(1) or id_match.group(0))
        for guild in bot.guilds or []:
            user = guild.get_member(user_id)
            if user is not None:
                break

        if user is None and not strict_guild:
            # user is not cached
            try:
                user = await bot.get_user_info(user_id)
            except discord.NotFound:
                pass

    if user is not None:
        return user if max_count == 1 else [user]

    if msg.guild is None:
        return None

    found = []
    pattern = pattern.lower()

    for member in msg.guild.members:
        match_pos = -1
        if member.nick is not None:
            match_pos = member.nick.lower().find(pattern)
        if match_pos == -1:
            # name#discrim
            match_pos = str(member).lower().find(pattern)
        if match_pos == -1:
            continue
        found.append((member, match_pos))

    found.sort(
        key=lambda x: (
            _get_last_user_message_timestamp(x[0].id, msg.channel.id, bot),
            -x[1],  # index of match in string
            x[0].status.name != 'offline',
            x[0].joined_at
        ), reverse=True
    )

    if found:
        return found[0][0] if max_count == 1 else [u for u, mp in found[:max_count]]

    return None


async def find_role(pattern, guild, bot, max_count=1):
    id_match = ROLE_OR_ID_REGEX.fullmatch(pattern)
    if id_match is not None:
        role_id = int(id_match.group(1) or id_match.group(0))
        # role = guild.get_role(role_id)
        # if role is not None:
        #     return role
        for role in guild.roles:
            if role.id == role_id:
                return role if max_count == 1 else [role]

    found = []
    pattern = pattern.lower()

    for role in guild.roles:
        match_pos = role.name.lower().find(pattern)
        if match_pos != -1:
            found.append((role, match_pos))

    found.sort(key=lambda x: x[1])

    if found:
        return found[0][0] if max_count == 1 else [r for r, mp in found[:max_count]]

    return None


async def find_guild(pattern, bot, max_count=1):
    id_match = ID_REGEX.fullmatch(pattern)
    if id_match is not None:
        guild_id = int(id_match.group(0))
        guild = bot.get_guild(guild_id)
        if guild is not None:
            return guild if max_count == 1 else [guild]

    found = []
    pattern = pattern.lower()

    for guild in bot.guilds:
        match_pos = guild.name.lower().find(pattern)
        if match_pos != -1:
            found.append((guild, match_pos))

    found.sort(
        key=lambda x: (x[0].member_count, x[1]),
        reverse=True
    )

    if found:
        return found[0][0] if max_count == 1 else [g for g, mp in found[:max_count]]

    return None

find_server = find_guild


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
        try:
            await msg.clear_reactions()
        except Exception:
            pass
        return None
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