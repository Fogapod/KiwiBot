BOT_OWNER_ID = 253384991940149249
DEV_GUILD_ID = 391987311468085248

DEV_GUILD_INVITE = 'https://discord.gg/TNXn8R7'

REPORT_CHANNEL_ID = 439532907195924491

ERROR_EXIT_CODE   = 1
STOP_EXIT_CODE    = 2
RESTART_EXIT_CODE = 3

ASCII_ART = (
    " _  ___        _ ___      _   \n"
    "| |/ (_)_ __ _(_) _ ) ___| |_ \n"
    "| ' <| \ V  V / | _ \/ _ \  _|\n"
    "|_|\_\_|\_/\_/|_|___/\___/\__|\n"
)


import re


ID_EXPR = '\d{17,19}'
USER_MENTION_EXPR = f'<@!?({ID_EXPR})>'
ROLE_MENTION_EXPR = f'<@&({ID_EXPR})>'
CHANNEL_MENTION_EXPR = f'<#({ID_EXPR})>'
EMOJI_EXPR = f'<(?P<animated>a?):(?P<name>[_a-zA-Z]{{2,32}}):(?P<id>{ID_EXPR})>'

ID_REGEX = re.compile(ID_EXPR)
USER_MENTION_REGEX = re.compile(USER_MENTION_EXPR)
ROLE_MENTION_REGEX = re.compile(ROLE_MENTION_EXPR)
CHANNEL_MENTION_REGEX = re.compile(CHANNEL_MENTION_EXPR)
EMOJI_REGEX = re.compile(EMOJI_EXPR)

USER_MENTION_OR_ID_REGEX = re.compile(f'(?:{USER_MENTION_EXPR})|{ID_EXPR}')
ROLE_OR_ID_REGEX = re.compile(f'(?:{ROLE_MENTION_EXPR})|{ID_EXPR}')
CHANNEL_OR_ID_REGEX = re.compile(f'(?:{CHANNEL_MENTION_EXPR})|{ID_EXPR}')

COLOUR_REGEX = re.compile('#?([a-f0-9]{6})', re.I)

TIME_REGEX = re.compile('''(?:(?:([0-9]{1,2})(?:years?|y))|
                           (?:([0-9]{1,2})(?:months?|mo))|
                           (?:([0-9]{1,4})(?:weeks?|w))|
                           (?:([0-9]{1,5})(?:days?|d))|
                           (?:([0-9]{1,5})(?:hours?|h))|
                           (?:([0-9]{1,5})(?:minutes?|m))|
                           (?:([0-9]{1,5})(?:seconds?|s)))
                           ''', re.VERBOSE + re.IGNORECASE)