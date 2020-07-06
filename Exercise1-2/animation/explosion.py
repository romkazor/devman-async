import asyncio
import curses
from tools.curses_tools import draw_frame, get_frame_size
from tools.sprites_tools import get_frames


EXPLOSION_FRAMES = get_frames('explosion')


async def explode(canvas, center_row, center_column):
    # rows, columns = get_frame_size(EXPLOSION_FRAMES[0])
    # corner_row = center_row - rows / 2
    # corner_column = center_column - columns / 2

    curses.beep()
    for frame in EXPLOSION_FRAMES:
        draw_frame(canvas, center_row, center_column, frame)

        await asyncio.sleep(0)
        draw_frame(canvas, center_row, center_column, frame, negative=True)
        await asyncio.sleep(0)
