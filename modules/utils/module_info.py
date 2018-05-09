from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from utils.funcs import create_subprocess_shell, execute_process, get_local_prefix
from constants import BOT_OWNER_ID, DEV_GUILD_INVITE, ASCII_ART

from discord import Colour, Embed
import discord

import os
import sys


class Module(ModuleBase):

    short_doc = 'Get information about me'

    name = 'info'
    aliases = (name, 'information', 'stats')
    category = 'Bot'
    bot_perms = (PermissionEmbedLinks(), )

    async def on_call(self, msg, args, **flags):
        git_url = None
        git_commit = None

        if os.path.isdir('.git'):
            program = ' && '.join((
                'git config --get remote.origin.url',
                'git show -s HEAD --format="latest commit made %cr by **%cn**: \`\`\`\n%s\n\`\`\`[commit %h]({repo_url}/commit/%H)"'
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
            repo_name = 'Unnamed Bot'

        try:
            user = await self.bot.get_user_info(BOT_OWNER_ID)
        except Exception:
            author = f'Not found! His id was {BOT_OWNER_ID}'
        else:
            author = str(user)

        e = Embed(
            colour=Colour.gold(), title='Information',
            url=git_url,
            description=(
                f'Hello, I\'m a discord bot created by **{author}**\n'
                f'```\n{ASCII_ART}```'
            )
        )
        if self.bot.is_dev:
            e.add_field(name='Warning', value='This is a dev instance of bot')
        e.add_field(
            name='Stats', value=(
                f'Bot is currently in **{len(self.bot.guilds)}** guilds with **{len(self.bot.users)}** unique users\n'
                f'**{len(tuple(self.bot.get_all_channels()))}** channels\n'
                f'**{len(self.bot.emojis)}** custom emojis\n'
                f'**{len(self.bot.shards)}** shards\n'
                f'**{len(self.bot.voice_clients)}** active voice connections'
            ), inline=False
        )
        e.add_field(
            name='Useful links', value=(
                f'[Support guild invite]({DEV_GUILD_INVITE})\n'
                f'[Github repository]({git_url})\n'
                f'[discordbots.org profile](https://discordbots.org/bot/{self.bot.user.id})'
            )
        )
        e.add_field(
            name='Environment status', value=(
                f'Python version: **{sys.version[:5]}**\n'
                f'discord.py version: **{discord.__version__}**'
            ), inline=False
        )
        e.add_field(name='git status', value=git_commit, inline=False)
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.set_footer(text='Local prefix: ' + await get_local_prefix(msg, self.bot))

        await self.send(msg, embed=e)