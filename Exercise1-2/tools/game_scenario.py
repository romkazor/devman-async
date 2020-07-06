import time

from animation.garbage import generate_garbage
from tools.sprites_tools import sleep, get_frames
from tools.curses_tools import draw_text_offset

PHRASES = {
    1957: "First Satellite",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: "Take the plasma gun! Shoot the garbage!",
}

space_data = {'YEAR': 1957}


def get_garbage_delay_tics(year):
    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2


async def run_scenario(canvas, coroutines):
    """Change year and add garbage"""
    start_time = last_time = int(time.time())
    row_max, _ = canvas.getmaxyx()
    frames = get_frames('garbage')

    while True:

        if (last_time - start_time) >= 1:
            space_data['YEAR'] += 1

        draw_text_offset(canvas, row_max - 3, space_data['YEAR'])
        for year in PHRASES:
            if year <= space_data['YEAR']:
                draw_text_offset(canvas, row_max - 2, PHRASES[year], text_max_len=50)

        delay = get_garbage_delay_tics(space_data['YEAR'])

        if delay:
            start_time = int(time.time())
            await sleep(delay)

            # Generate and add space garbage animation to coroutines
            await generate_garbage(canvas, frames, coroutines)
        else:
            await sleep(10)

        last_time = int(time.time())
