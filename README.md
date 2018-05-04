# KiwiBot
<img align=right height=256 src=.github/avatar.png/>
Bot is currently in early stage of development, but it's already usable and has several useful commands.

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
* [aioredis python library](https://dateutil.readthedocs.io/en/stable)
* running [redis server](https://redis.io) on default port
