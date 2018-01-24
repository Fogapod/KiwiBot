import asyncio


async def execute_subprocess(*args, msg=None, bot=None):
        process = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE,
                   stderr=asyncio.subprocess.PIPE
        )

        print('Started task:', args, '(pid = ' + str(process.pid) + ')')

        if msg is not None:
            start_message = await bot.send_message(
                msg.channel, 'Started task with pid `' + str(process.pid) + '`',
                response_to=msg
            )
        else:
            start_message = None

        stdout, stderr = await process.communicate()

        print('Completed:', args, '(pid = ' + str(process.pid) + ')')

        result = stdout.decode().strip()

        if process.returncode != 0:
            result += '\n' + stderr.decode()

        return result, start_message