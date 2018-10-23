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
        # returns (amount of requests left, seconds until

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

        key = f'ratelimit:{self.name}:{target_id}'
        amount = await ctx.bot.redis.incr(key)

        if amount == 1:  # was createdt
            await ctx.bot.redis.expire(key, self.time)

        return self.amount - amount + 1, await ctx.bot.redis.ttl(key)
