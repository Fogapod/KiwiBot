from modules.modulebase import ModuleBase

from permissions import PermissionEmbedLinks
from utils.helpers import (
    create_subprocess_shell, execute_process, get_local_prefix)
from utils.constants import BOT_OWNER_ID

from discord import Colour, Embed
import discord

import os
import sys


class Module(ModuleBase):

    short_doc = 'Get information about me.'

    name = 'info'
    aliases = (name, 'information', 'stats')
    required_perms = (PermissionEmbedLinks, )

    async def on_call(self, msg, *args, **flags):
        git_url = None
        git_commit = None

        if os.path.isdir('.git'):
            program = ' && '.join((
                'git config --get remote.origin.url',
                'git show -s HEAD --format="latest commit made %cr by [%an]({domain}/%an): \`\`\`\n%s\n\`\`\`[commit %h]({repo_url}/commit/%H)"'
            ))
            process, pid = await create_subprocess_shell(program)
            stdout, stderr = await execute_process(process, program)
            git_url, _, git_commit = stdout.decode().strip().partition('\n')

            if git_url.endswith('.git'):
                git_url = git_url[:-4]
            if git_url.startswith('ssh://'):
                git_url = git_url[6:]
            if git_url.startswith('git@'):
                domain, _, resource = git_url[4:].partition(':')
                git_url = f'https://{domain}/{resource}'
            if git_url.endswith('/'):
                git_url = git_url[:-1]

            git_domain = 'https://' + git_url[8:].split('/')[0]
            git_commit = git_commit.format(repo_url=git_url, domain=git_domain)
            repo_name = git_url.split('/')[-1]
        else:
            git_url = 'https://github.com/Fogapod/BotMyBot'
            git_commit = 'Could not get information.'
            repo_name = 'NameBotName'

        try:
            user = await self.bot.get_user_info(BOT_OWNER_ID)
        except Exception:
            author = f'Not found! His id was {BOT_OWNER_ID}'
        else:
            author = str(user)

        prefix = await get_local_prefix(msg, self.bot)

        embed = Embed(
            colour=Colour.gold(), title=repo_name,
            url=git_url,
            description=(
                f'Hello, my name is **{repo_name}**!\n'
                f'I\'m a discord bot created by **{author}**'
            )
        )
        embed.add_field(
            name='Here is some useful info about me', value=(
                f'Local prefix: **{prefix}**\n'
                f'Bot is currently in **{len(self.bot.guilds)}** guilds with **{len(self.bot.users)}** unique users'
            ), inline=False
        )
        embed.add_field(
            name='environment status', value=(
                f'Python version: **{sys.version[:5]}**\n'
                f'discord.py version: **{discord.__version__}**'
            ), inline=False
        )
        embed.add_field(name='git status', value=git_commit, inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        await self.send(msg, embed=embed)