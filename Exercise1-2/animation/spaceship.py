import asyncio
from math import fabs

from animation.fire import fire
from animation.garbage import obstacles, obstacles_damaged
from animation.gameover import show_gameover
from tools.curses_tools import draw_frame, read_controls, get_frame_size, draw_text_offset
from tools.physics import update_speed
from tools.sprites_tools import get_frames
from tools.game_scenario import space_data


SPACESHIP_FRAMES = get_frames('rocket')
GAMEOVER_FRAMES = get_frames('gameover')
ship_data = {'position': [0, 0], 'covered_distance': 0, 'spaceship_frame': None}


async def run_spaceship(canvas, row, column, coroutines):
    """Control of spaceship."""

    row_max, column_max = canvas.getmaxyx()
    frame_row, frame_column = get_frame_size(SPACESHIP_FRAMES[0])
    row_speed = column_speed = 0

    while True:

        # Set position(coordinates/speed) of spaceship
        rows_direction, columns_direction, space = read_controls(canvas)
        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)
        row += row_speed
        column += column_speed

        # Up and Down restrict and teleportation
        screen_border = 2
        if row < screen_border - frame_row:
            row = row_max - screen_border
        elif row > row_max - screen_border:
            row = screen_border - frame_row
        # Right and Left restrict and teleportation
        if column > column_max - screen_border:
            column = screen_border - frame_column
        elif column < screen_border - frame_column:
            column = column_max - screen_border

        if space and space_data['YEAR'] >= 2020:
            coroutines.append(fire(canvas, row, column + 2))

        # Game over if collision
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_damaged.append(obstacle)
                coroutines.append(show_gameover(canvas, GAMEOVER_FRAMES))
                return

        # Ship distance calculation
        ship_data['covered_distance'] += fabs(row_speed) + fabs(column_speed)
        # Show advanced information (coordinates and distance)
        coordinates = f"{str(round(row))}, {str(round(column))}"
        covered_distance = int(ship_data['covered_distance'])
        covered_distance_str = f"{covered_distance} km"
        draw_text_offset(canvas, 1, coordinates, text_max_len=12)
        draw_text_offset(canvas, 2, covered_distance_str)

        # Draw spaceship animation
        draw_frame(canvas, row, column, ship_data['spaceship_frame'])
        old_frame = ship_data['spaceship_frame']
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, old_frame, negative=True)


async def animate_spaceship():
    """Update spaceship frame"""

    while True:
        for frame in SPACESHIP_FRAMES:
            ship_data['spaceship_frame'] = frame
            await asyncio.sleep(0)
