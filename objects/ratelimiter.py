EXISTING_TYPES = ('global', 'guild', 'channel', 'user')


class Ratelimiter:
    def __init__(self, rl_type, name, amount, time=60):
        if rl_type not in EXISTING_TYPES:
            raise ValueError('Unknown ratelimiter type')

        self.rl_type = rl_type
        self.name = name
        self.amount = amount
        self.time = time

    async def test(self, ctx):
        # returns (amount of requests left, milliseconds until ratelimit expires)

        key = self._get_key(ctx)
        amount = await ctx.bot.redis.incr(key)

        if amount == 1:  # was created
            await ctx.bot.redis.expire(key, self.time)

        return self.amount - amount + 1, await ctx.bot.redis.pttl(key)

    async def clear(self, ctx):
        await ctx.bot.redis.delete(self._get_key(ctx))

    async def decrease_time(self, amount, ctx):
        key = self._get_key(ctx)
        ttl = await ctx.bot.redis.ttl(key)
        if ttl > 0:
            await ctx.bot.redis.expire(key, ttl - amount)

    async def increase_time(self, amount, ctx):
        key = self._get_key(ctx)
        ttl = await ctx.bot.redis.ttl(key)
        if ttl > 0:
            await ctx.bot.redis.expire(key, ttl + amount)

    def _get_key(self, ctx):
        if self.rl_type == 'global':
            target_id = ''
        elif self.rl_type == 'guild':
            target_id = ctx.guild.id
        elif self.rl_type == 'channel':
            target_id = ctx.channel.id
        elif self.rl_type == 'user':
            target_id = ctx.author.id
        else:
            raise ValueError('Invalid ratelimiter type')

        return  f'ratelimit:{self.name}:{target_id}'
