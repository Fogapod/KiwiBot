from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks
from objects.paginators import Paginator

from discord import Colour, Embed

from utils.funcs import request_reaction_confirmation


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <subcommand>'
    short_doc = 'Anonymous chat'
    long_doc = (
        'Subcommands:\n'
        '\t[say|send] <text>: send message to current room\n'
        '\t[new|create]: enter queue for the new room\n'
        '\t[leave|close] <room id>: exit room\n'
        '\t[connect|set] <room id>: switch to different room\n'
        '\tlist: show list of chats you\'re in\n\n'
        'To use chat, create room first usinng {prefix}{aliases} new\n'
        'After 2nd user connects, you can communicate using {prefix}{aliases} say <text>\n\n'
        'If you want to move conversation to different channel, use {prefix}{aliases} connect <room id> in that channel\n\n'
        'To quit room, use {prefix}{aliases} close <room id>'
    )

    name = 'chat'
    aliases = (name,)
    category = 'Actions'
    min_args = 1
    bot_perms = (PermissionEmbedLinks(), )

    async def on_load(self, from_reload):
        if not await self.bot.redis.exists('last_chat_room_id'):
            await self.bot.redis.set('last_chat_room_id', '0')

    async def on_call(self, ctx, args, **flags):
        subcommand = args[1].lower()

        if subcommand in ('say', 'send'):
            room_id = await self.bot.redis.get(f'room_id_by_channel_and_user:{ctx.channel.id}:{ctx.author.id}')
            if room_id is None:
                return await ctx.warn('Your message wasn\'t delivered. Please, connect to chat room first')
            
            u1_target_channel, u2_target_channel = await self.bot.redis.smembers(f'chat_room:{room_id}')

            user2_id = (u2_target_channel if u1_target_channel.endswith(str(ctx.author.id)) else u1_target_channel).split(':')[1]
            target_channel_id = (u1_target_channel if u1_target_channel.endswith(user2_id) else u2_target_channel).split(':')[0]

            user2 = self.bot.get_user(int(user2_id))
            target = self.bot.get_channel(int(target_channel_id))

            if target is None:
                target = user2
                if target is None:
                    return await ctx.error('2nd user not found! Please, try again')

            e = Embed(title='KiwiBot anonymous chat', description=args[2:], colour=Colour.gold())
            e.set_author(name=user2, icon_url=user2.avatar_url)
            e.set_footer(text=f'Room id: {room_id}')

            try:
                await target.send(embed=e)
            except Exception:
                return await ctx.send('Failed to deliver message')
            else:
                return await ctx.react('✅')

        elif subcommand in ('connect', 'set'):
            if len(args) < 3:
                return await self.on_doc_request(ctx)

            try:
                room_id = int(args[2])
            except ValueError:
                return await ctx.error('Chat id is not digit')

            room = await self.bot.redis.smembers(f'chat_room:{room_id}')
            if room:
                u1_target_channel, u2_target_channel = room
                if u1_target_channel.endswith(str(ctx.author.id)) or u2_target_channel.endswith(str(ctx.author.id)):
                    if u1_target_channel.endswith(str(ctx.author.id)):
                        old_member = u1_target_channel
                        user2_id = u2_target_channel.split(':')[1]
                    else:
                        old_member = u2_target_channel
                        user2_id = u1_target_channel.split(':')[1]

                    new_user1_channel = f'{ctx.channel.id}:{ctx.author.id}'

                    await self.bot.redis.delete(f'room_id_by_channel_and_user:{old_member}')
                    await self.bot.redis.set(f'room_id_by_channel_and_user:{new_user1_channel}', room_id)

                    await self.bot.redis.srem(f'chat_room:{room_id}', old_member)
                    await self.bot.redis.sadd(f'chat_room:{room_id}', new_user1_channel)

                    return await ctx.send(f'Connected to room #{room_id}')

            return await ctx.warn('You\'re not a room member or room does not exist')

        elif subcommand in ('new', 'create'):
            waiting_user = await self.bot.redis.get('waiting_chat_user')
            if waiting_user is None:
                await self.bot.redis.set('waiting_chat_user', f'{ctx.channel.id}:{ctx.author.id}')
                return await ctx.send('Please, wait for 2nd user to connect. This might take a while')

            channel_id, user_id = waiting_user.split(':')
            if int(user_id) == ctx.author.id:
                return await ctx.warn('You\'re already queued. Please, wait for the 2nd user to connect')

            await self.bot.redis.delete('waiting_chat_user')

            user2 = self.bot.get_user(int(user_id))
            target = self.bot.get_channel(int(channel_id))

            if target is None:
                target = user2
                if target is None:
                    return await ctx.error('2nd user not found! Please, try again')

            new_room_id = int(await self.bot.redis.incr('last_chat_room_id'))

            user1_channel = f'{ctx.channel.id}:{ctx.author.id}'
            user2_channel = f'{channel_id}:{user_id}'

            await self.bot.redis.sadd(f'chat_room:{new_room_id}',user1_channel, user2_channel)

            await self.bot.redis.set(f'room_id_by_channel_and_user:{user1_channel}', new_room_id)
            await self.bot.redis.set(f'room_id_by_channel_and_user:{user2_channel}', new_room_id)

            e = Embed(title=f'Created chat room #{new_room_id}', colour=Colour.gold())
            e.set_footer(text=user2, icon_url=user2.avatar_url)
            e.description  = 'Now you can send messages with `chat say`'

            failed_to_notify = False

            try:
                await target.send(embed=e)
            except Exception:
                if not target == user2:
                    try:
                        await self.bot.get_user(int(user_id)).send(embed=e)
                    except Exception:
                        failed_to_notify = True
                else:
                    failed_to_notify = True

            if failed_to_notify:
                e.description += 'Warning: failed to notify 2nd user about chat creation'

            e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=e)

        elif subcommand in ('leave', 'close'):
            if len(args) < 3:
                return await self.on_doc_request(ctx)

            try:
                room_id = int(args[2])
            except ValueError:
                return await ctx.error('Chat id is not digit')

            room = await self.bot.redis.smembers(f'chat_room:{room_id}')
            if room:
                u1_target_channel, u2_target_channel = room
                if u1_target_channel.endswith(str(ctx.author.id)) or u2_target_channel.endswith(str(ctx.author.id)):
                    confirm_msg = await ctx.send(
                        (
                            f'Are you sure you want to close chat **#{room_id}** ?\n'
                            f'**This action cannot be undone**\n'
                            f'If you want to move chat to different channel, use `connect` subcommand instead\n'
                            f'React with ✅ to continue'
                        )
                    )

                    if not await request_reaction_confirmation(confirm_msg, ctx.author):
                        return await self.bot.edit_message(confirm_msg, f'Cancelled closing of chat **#{room_id}**')

                    await self.bot.redis.delete(
                        f'chat_room:{room_id}',
                        f'room_id_by_channel_and_user:{u1_target_channel}',
                        f'room_id_by_channel_and_user:{u2_target_channel}'
                    )

                    return await self.bot.edit_message(confirm_msg, f'**{ctx.author}** closed chat **#{room_id}**')

            return '{warning} You\'re not a room member or room does not exist'

        elif subcommand == 'list':
            keys = await self.bot.redis.keys('chat_room:*')

            lines = []
            for k in keys:
                u1_target_channel, u2_target_channel = await self.bot.redis.smembers(k)
                if u1_target_channel.endswith(str(ctx.author.id)) or u2_target_channel.endswith(str(ctx.author.id)):
                    lines.append(f'#{k[10:]}' )

            if not lines:
                return 'No active chats found'

            lines_per_chunk = 30
            chunks = ['```\n' + '\n'.join(lines[i:i + lines_per_chunk]) + '```' for i in range(0, len(lines), lines_per_chunk)]

            p = Paginator(self.bot)
            for i, chunk in enumerate(chunks):
                e = Embed(
                    title='Active chats',
                    colour=Colour.gold(),
                    description=chunk
                )
                e.set_footer(text=f'Page {i + 1} / {len(chunks)}')
                p.add_page(embed=e)

            return await p.run(ctx)

        else:
            return await ctx.warn('Unknown subcommand')
