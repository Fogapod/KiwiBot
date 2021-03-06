import psutil

from objects.modulebase import ModuleBase

import random
import time
import os

from math import sin, cos, pi

from PIL import Image

import discord

from utils.funcs import find_image, create_subprocess_exec, execute_process


DEG_TO_RAD_RATIO = pi / 180

# fly image side (square)
FLY_SIDE = 60

# degrees to first digit of file name, approximately
DIRECTIONS = {
    120: '1',
     75: '2',
     30: '3',
    345: '4',
    300: '5',
    255: '6',
    210: '7',
    165: '8'
}

# state of legs
FIRST_STATE = 1
FINAL_STATE = 6

# max allowed side of input image
MAX_SIDE = 512

GIFSICLE_ARGUMENTS = ['gifsicle', '--optimize=3', '--batch', '--careful']

class ImageTooSmall(Exception):
    pass


class Fly:

    def __init__(self, speed=1.0):
        self.speed = speed

        self.pos_x = 0
        self.pos_y = 0

        self.bounds_x = (0, 0)
        self.bounds_y = (0, 0)

        self.angle = list(DIRECTIONS.keys())[0]
        self.state = FIRST_STATE

        self._modified = True

    def _rand_pos(self):
        return (
            random.randint(*self.bounds_x),
            random.randint(*self.bounds_y)
        )

    def _move_forward(self):
        angle = self.angle * DEG_TO_RAD_RATIO
        new_x = self.pos_x + round(cos(angle) * self.speed)
        new_y = self.pos_y - round(sin(angle) * self.speed)

        if not (
            (self.bounds_x[0] <= new_x <= self.bounds_x[1]) and
            (self.bounds_y[0] <= new_y <= self.bounds_y[1])
        ):

            new_x = min(self.bounds_x[1], max(self.bounds_x[0], new_x))
            new_y = min(self.bounds_y[1], max(self.bounds_y[0], new_y))
            if self.angle > 270:
                self.angle = list(DIRECTIONS.keys())[0]
            else:
                self.angle += 90

        elif (new_x, new_y) != (self.pos_x, self.pos_y):
            self._modifieed = True

        self.pos_x, self.pos_y = new_x, new_y

    def _rand_angle(self):
        return random.choice(list(DIRECTIONS.keys()) + [self.angle])

    def _increment_state(self):
        if self.state >= FINAL_STATE:
            self.state = FIRST_STATE
        else:
            self.state += 1

        self._modified = True

    def spawn(self, bounds_x, bounds_y):
        self.bounds_x, self.bounds_y = bounds_x, bounds_y

        self.pos_x, self.pos_y = self._rand_pos()
        self.angle = self._rand_angle()
        self.state = FIRST_STATE

        self._modified = True

    def do_step(self):
        # actions:
        #   0: do not move
        #   1: rotate to target
        #   2: move

        actions = (  0,   1,  2)
        weights = (.15, .15, .7)

        action = random.choices(actions, weights)[0]
        if action == 0:
            return
        elif action == 1:
            self.angle = self._rand_angle()
        elif action == 2:
            self._move_forward()

        self._increment_state()

        self._modified = True

class FlyDrawer:

    def __init__(self, source, flies, steps=100, fly_source=None):
        self.source = source.convert('RGBA')
        self.source.thumbnail((MAX_SIDE, MAX_SIDE), Image.ANTIALIAS)

        if fly_source:
            self.fly_source = fly_source.convert('RGBA')
            self.fly_source.thumbnail((FLY_SIDE, FLY_SIDE), Image.ANTIALIAS)
        else:
            self.fly_source = None

        for coordinate in self.source.size:
            if FLY_SIDE > coordinate:
                raise ImageTooSmall

        self.flies = flies
        self.steps = steps

        bounds_x = (0, self.source.size[0] - FLY_SIDE)
        bounds_y = (0, self.source.size[1] - FLY_SIDE)
        for fly in self.flies:
            fly.spawn(bounds_x, bounds_y)

        self._cached_flies = {}
        self._frames = []

    def _get_fly_image(self, angle, state):
        name = f'{DIRECTIONS[angle]}_{state if not self.fly_source else 0}'
        if name in self._cached_flies:
            img = self._cached_flies[name]
        else:
            if self.fly_source:
                img = self.fly_source.rotate(angle, expand=True)
            else:
                img = Image.open(f'templates/flies/{name}')

            self._cached_flies[name] = img

        return img

    def make_frame(self):
        modified = False
        for fly in self.flies:
            if fly._modified:
                modified = True
                break

        if not modified:
            self._frames.append(self._frames[-1].copy())
            return


        overlay = self.source.copy()

        for fly in self.flies:
            fly._modified = False
            img = self._get_fly_image(fly.angle, fly.state)
            overlay.alpha_composite(img, (fly.pos_x, fly.pos_y))

        self._frames.append(overlay)

    def cleanup(self):
        for frame in self._frames:
            frame.close()

        for image in self._cached_flies.values():
            image.close()

        self.source.close()
        if self.fly_source:
            self.fly_source.close()

    def run(self):
        for i in range(self.steps):
            for fly in self.flies:
                fly.do_step()

            self.make_frame()

        filename = f'/tmp/fly_{time.time()}.gif'
        self._frames[0].save(
            filename, format='GIF', optimize=True, save_all=True,
            append_images=self._frames[1:], loop=0 #, disposal=2 # currently broken in Pillow
        )

        self.cleanup()

        return filename


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [image]'
    short_doc = 'Simulates fly on image'
    long_doc = (
        'Flags:\n'
        '\t[--steps|-s]    <steps>:  amount of steps to simulate. Default is 100\n'
        '\t[--velocity|-v] <speed>:  speed of flies in pixels. Default is 10\n'
        '\t[--amount|-a]   <amount>: number of flies on imagei\n'
        '\t[--image|-i]    <image>:  use this image instead of flies'
    )

    name = 'fly'
    aliases = (name, )
    category = 'Images'
    flags = {
        'steps': {
            'alias': 's',
            'bool': False
        },
        'velocity': {
            'alias': 'v',
            'bool': False
        },
        'amount': {
            'alias': 'a',
            'bool': False
        },
        'image': {
            'alias': 'i',
            'bool': False
        }
    }
    ratelimit = (1, 7)

    async def on_call(self, ctx, args, **flags):
        image = await find_image(args[1:], ctx, include_gif=False)
        source = await image.to_pil_image()
        if image.error:
            return await ctx.warn(f'Error getting image: {image.error}')

        fly_source = None
        image_flag = flags.get('image')
        if image_flag is not None:
            fly_img = await find_image(image_flag, ctx, include_gif=False)
            fly_source = await fly_img.to_pil_image()
            if fly_img.error:
                return await ctx.warn(f'Error getting fly image: {fly_img.error}')

        try:
            steps = int(flags.get('steps', 100))
        except ValueError:
            return await ctx.error('Failed to convert steps flag value to integer')

        if not (1 <= steps <= 200):
            return await ctx.error('Number of steps should be between 1 and 200')

        try:
            velocity = float(flags.get('velocity', 10))
        except (ValueError, OverflowError):
            return await ctx.error('Failed to convert velocity flag value to float')

        if not (1 <= velocity <= 50):
            return await ctx.error('Velocity should be between 1 and 50')

        try:
            amount = int(flags.get('amount', 1))
        except ValueError:
            return await ctx.error('Failed to convert amount flag value to integer')

        if not (1 <= amount <= 20):
            return await ctx.error('Amount should be between 1 and 20')

        process = psutil.Process()

        async with ctx.channel.typing():
            mem_start = process.memory_info().rss
            try:
                 filename = await self.bot.loop.run_in_executor(
                    None, self.draw, source, steps, velocity, amount, fly_source)
            except ImageTooSmall:
                return await ctx.warn('Image is too small')

            # optimize gif using gifsicle
            proc, _ = await create_subprocess_exec(*GIFSICLE_ARGUMENTS + [filename])
            await execute_process(proc)

        mem_stats = f'Memory wasted: **{round(process.memory_info().rss - mem_start >> 20, 3)} MB**'
        await ctx.send(mem_stats, file=discord.File(filename, filename='fly.gif'))

        os.remove(filename)  # blocking

    def draw(self, source, steps, speed, amount, fly_source):
        flies = []
        for i in range(amount):
            flies.append(Fly(speed=speed))

        filename = FlyDrawer(source, flies, steps=steps, fly_source=fly_source).run()
        source.close()
        if fly_source:
            fly_source.close()

        return filename
