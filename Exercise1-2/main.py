import time
import random
import curses
from curses import wrapper, curs_set

from animation.stars import blink
from animation.spaceship import animate_spaceship, run_spaceship, SPACESHIP_FRAMES
from animation.garbage import scores
from tools.curses_tools import get_center, draw_text_offset
from tools.game_scenario import run_scenario
from settings import TIC_TIMEOUT, STARS_FREQ_PERCENT

coroutines = []


def set_canvas_settings(canvas, sleep):
    """Apply canvas settings: border, refresh, sleep"""

    canvas.border()
    canvas.refresh()
    time.sleep(sleep)


def draw_main(canvas):
    """Main logic"""

    curs_set(False)
    canvas.nodelay(True)

    row_max, column_max = canvas.getmaxyx()
    screen_border = 2

    # Generate and add stars blink animation to coroutines
    stars_max = int(row_max * column_max * STARS_FREQ_PERCENT / 100)
    row_max_fix = row_max - screen_border
    column_max_fix = column_max - screen_border
    for _ in range(stars_max):
        coroutines.append(blink(canvas, random.randint(1, row_max_fix), random.randint(1, column_max_fix),
                                symbol=random.choice(['+', '*', '.', ':']), timeout=random.randint(0, 20)))

    # Add spaceship animation to coroutines (on center)
    center_row, center_column = get_center(canvas, SPACESHIP_FRAMES)
    coroutines.append(animate_spaceship())
    coroutines.append(run_spaceship(canvas, center_row, center_column, coroutines))

    # Starting countdown years
    coroutines.append(run_scenario(canvas, coroutines))

    # Start main loop of the game
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)

            except StopIteration:
                coroutines.remove(coroutine)
            except (SystemExit, KeyboardInterrupt):
                exit(0)

        # Show progress
        draw_text_offset(canvas, 4, 'score:', text_max_len=7)
        draw_text_offset(canvas, 5, scores['points'])

        set_canvas_settings(canvas, TIC_TIMEOUT)


def main():
    curses.update_lines_cols()
    wrapper(draw_main)


if __name__ == '__main__':
    main()
