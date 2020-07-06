import curses

from tools.sprites_tools import sleep
from settings import TIC_TIMEOUT


async def blink(canvas, row, column, symbol='*', timeout=1):
    """Display animation of star blink. Symbol of star and timeout can be specified."""

    await sleep(timeout)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(2 / TIC_TIMEOUT)

        canvas.addstr(row, column, symbol)
        await sleep(0.3 / TIC_TIMEOUT)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(0.5 / TIC_TIMEOUT)

        canvas.addstr(row, column, symbol)
        await sleep(0.3 / TIC_TIMEOUT)
