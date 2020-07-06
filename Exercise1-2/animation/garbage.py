import random
import asyncio

from animation.explosion import explode
from tools.curses_tools import draw_frame, get_frame_size
from tools.obstacles import Obstacle

obstacles = []
obstacles_damaged = []
scores = {'points': 0}


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    rows_size, columns_size = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, rows_size, columns_size)
    obstacles.append(obstacle)

    try:
        while row < rows_number:
            draw_frame(canvas, row, column, garbage_frame)

            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed

            obstacle.row = row

            # Remove obstacle if hit
            if obstacle in obstacles_damaged:
                obstacles_damaged.remove(obstacle)
                scores['points'] += 1
                await explode(canvas, row, column)
                return

    finally:
        obstacles.remove(obstacle)


async def generate_garbage(canvas, frames, coroutines):
    """Generate and add random space garbage animation to coroutines"""
    _, column_max = canvas.getmaxyx()
    frame = random.choice(frames)
    random_column = random.randint(1, column_max)

    garbage_coroutine = fly_garbage(canvas, random_column, frame)
    coroutines.append(garbage_coroutine)
