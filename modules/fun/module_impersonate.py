from objects.modulebase import ModuleBase
from objects.permissions import PermissionBotOwner, PermissionManageWebhooks

from utils.funcs import find_user, find_channel


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <user> <text>'
    short_doc = 'Impersonate someone'
    long_doc = (
        'Command flags:\n'
        '\t[--channel|-c] <channel>: Channel where to send message'
    )

    name = 'impersonate'
    aliases = (name, )
    category = 'Actions'
    min_args = 2
    bot_perms = (PermissionManageWebhooks(), )
    flags = {
        'channel': {
            'alias': 'c',
            'bool': False
        }
    }

    async def on_call(self, ctx, args, **flags):
        user = await find_user(args[1], ctx.message)

        if user is None:
            return '{warning} User not found'

        channel = flags.get('channel', None)

        if channel:
            channel = await find_channel(
                channel, ctx.guild, include_voice=False, include_category=False)

            if channel is None:
                return '{warning} Channel not found'

        if channel is None:
            channel = ctx.channel

        if not channel.permissions_for(ctx.author).send_messages:
            return '{warning} You don\'t have permission to send messages to this channel'

        name = user.display_name if getattr(user, 'guild', None) == ctx.guild else user.name

        if len(name) < 2:
            # minimum webhook name len is 2 characters, so transparent character is required
            name = ' ุ' + name

        try:
            webhook = await channel.create_webhook(name=name)
            #
            # https://github.com/Rapptz/discord.py/issues/1242
            #
            webhook._adapter.store_user = webhook._adapter._store_user
        except Exception:
            return '{error} Failed to create webhook. Probably maximum webhook count reached'

        try:
            await self.bot.send_message(
                webhook, args[2:],
                avatar_url=user.avatar_url_as(format='png'),
                wait=True, response_to=ctx.message
            )
        except Exception:
            pass

        await webhook.delete()
