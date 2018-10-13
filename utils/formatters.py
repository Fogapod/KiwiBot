import re

import discord

from constants import USER_MENTION_REGEX, ROLE_MENTION_REGEX


async def format_response(response, message, bot):
    format_dict = {}

    if '{warning}' in response:
        format_dict['warning'] = '⚠'
    if '{error}' in response:
        format_dict['error'] = '❗'
    # if '{guild}' in response and message.guild:
    #     format_dict['guild'] = message.guild.name
    # if '{guild_id}' in response and message.guild:
    #     format_dict['guild_id'] = message.guild.id
    # if '{channel}' in response:
    #     format_dict['channel'] = getattr(message.channel, 'name', 'DMchannel')
    # if '{channel_id}' in response:
    #     format_dict['channel_id'] = message.channel.id
    # if '{id}' in response:
    #     format_dict['id'] = message.author.id
    # if '{name}' in response:
    #     format_dict['name'] = message.author.name
    # if '{nick}' in response:
    #     format_dict['nick'] = message.author.display_name
    # if '{discrim}' in response:
    #     format_dict['discrim'] = message.author.discriminator
    # if '{mention}' in response:
    #     format_dict['mention'] = message.author.mention

    return lazy_format(response, **format_dict)


def trim_text(text, max_len=2000):
    text = text.strip()
    if len(text) > max_len:
        return text[:max_len // 2 - 3] + '\n...\n' + text[-max_len // 2 + 2:]

    return text


async def replace_mentions(content, channel, bot):
    for mid in USER_MENTION_REGEX.findall(content):
        mid = int(mid)
        user = None

        if getattr(channel, 'guild', None) is not None:
            user = channel.guild.get_member(mid)
        if user is None:
            user = discord.utils.get(bot.users, id=mid)
        if user is None:
            try:
                user = await bot.get_user_info(mid)
            except discord.NotFound:
                continue

        content = re.sub(f'<@!?{user.id}>', f'@{user}', content)

    for rim in ROLE_MENTION_REGEX.findall(content):
        rim = int(rim)
        if getattr(channel, 'guild', None) is not None:
            role = discord.utils.get(channel.guild.roles, id=rim)
        else:
            break

        if role is None:
            continue

        content = content.replace(f'<@&{role.id}>', f'@{role}')

    return content


def replace_mass_mentions(text):
	return text.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')


def lazy_format(s, *args, **kwargs):
    while True:
        try:
            return s.format(*args, **kwargs)
        except KeyError as e:
            key = e.args[0]
            kwargs[key] = "{%s}" % key
        except (ValueError, AttributeError, IndexError, TypeError):
            return s

def cleanup_code(text):
    lang = None
    if len(text) > 6 and text[:3] == '```' and text[-3:] == '```':
        text = text[3:-3]
        lang = ''
        for i, c in enumerate(text):
            if c.isspace():
                if c == '\n':
                    break
            else:
                lang += c
        text = text[i + 1:]
    return text, lang
