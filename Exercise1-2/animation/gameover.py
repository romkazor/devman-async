from tools.sprites_tools import sleep
from tools.curses_tools import get_frame_size, draw_frame, get_center
from settings import TIC_TIMEOUT


async def show_gameover(canvas, frames):
    """Display GAMEOVER frames animation."""
    center_row, center_column = get_center(canvas, frames)

    while True:
        for frame in frames:
            draw_frame(canvas, center_row, center_column, frame)
            await sleep(0.5 / TIC_TIMEOUT)

            draw_frame(canvas, center_row, center_column, frame, negative=True)
            await sleep(0.1 / TIC_TIMEOUT)
