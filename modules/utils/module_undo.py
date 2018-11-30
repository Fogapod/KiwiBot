from objects.modulebase import ModuleBase


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [amount]'
    short_doc = 'Removes previous command and responses'

    name = 'undo'
    aliases = (name, )
    category = 'Actions'
    max_args = 1

    async def on_call(self, ctx, args, **flags):
        response = ''

        if len(args) == 2:
            if not args[1].isdigit():
                return await ctx.warn(
                    'Amount must be a positive number',
                    register=False, delete_after=4
                )
            amount = int(args[1])
        else:
            amount = 1

        deleted = 0
        failed = 0

        async for msg in ctx.channel.history(
                limit=100, before=ctx.message.edited_at or ctx.message.created_at):

            if amount == 0:
                break

            if msg.author != ctx.author:
                continue

            if len(await self.bot.redis.lrange(f'tracked_message:{msg.id}', 1, -1)):
                try:
                    await self.bot.delete_message(msg, raise_on_errors=True)
                except Exception:  # do cleanup manually
                    failed += 1
                    await self.bot.clear_responses_to_message(msg.id)

                deleted += 1
                amount -= 1

        await self.bot.send_message(
            ctx.channel,
            f'Deleted responses to **{deleted}** command(s), failed to delete **{failed}** messages',
            delete_after=4,
        )

        await self.bot.delete_message(ctx.message)
