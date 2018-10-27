# KiwiBot

<img align=right height=256 src=.github/avatar.png>

Note: Please, read [this](https://github.com/WorstDiscordBots/KiwiBot/blob/master/README.md) before using bot.

You can add bot to your guild [with](https://discordapp.com/oauth2/authorize?client_id=394793577160376320&scope=bot&permissions=8) or [without](https://discordapp.com/oauth2/authorize?client_id=394793577160376320&scope=bot&permissions=2146958583) administrator permision.

Bot is developed by **Eugene#3778**.  
You can dm me any time or join development guild to ask help / questions: https://discord.gg/TNXn8R7  
Default prefix is `+`, you can also mention bot to use command.  
Use `help` command to get list of available commands.

## Running bot
You can run bot with `bash run.sh` file from root directory.  
Requirements:
* [python >= 3.6](https://www.python.org/downloads)
* [discord.py python library, rewrite branch](https://github.com/Rapptz/discord.py/tree/rewrite)
* [dateutil python library](https://dateutil.readthedocs.io/en/stable)
* [aioredis python library](https://aioredis.readthedocs.io/en/v1.1.0)
* [uvloop python library](https://uvloop.readthedocs.io)
* running [redis server](https://redis.io) on default port
* And other libraries used in commands
