from objects.modulebase import ModuleBase


class Module(ModuleBase):

    short_doc = 'Removes previous command and responses'

    name = 'undo'
    aliases = (name, )
    category = 'Actions'

    async def on_call(self, ctx, args, **flags):
        async for msg in ctx.channel.history(
                limit=200, before=ctx.message.edited_at or ctx.message.created_at):

            if msg.author != ctx.author or msg.id == ctx.message.id:
                continue

            if len(await self.bot.redis.lrange(f'tracked_message:{msg.id}', 1, -1)):
                try:
                    await self.bot.delete_message(msg, raise_on_errors=True)
                except Exception:  # do cleanup manually
                    await self.bot.clear_responses_to_message(msg)

                await self.bot.delete_message(ctx.message)

                return await ctx.send(
                    'Deleted last command and corresponding responses',
                    register=False, delete_after=5
                )

        return '{warning} No commands found in the last 200 messages. Try deleting them manually'
