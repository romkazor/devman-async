import asyncio
import os


def get_frames(sprite_directory):
    """Get spaceship sprites"""

    sprites = []

    for file in os.listdir(f"sprites/{sprite_directory}"):
        with open(f"sprites/{sprite_directory}/{file}", "r") as my_file:
            sprite = my_file.read()
            sprites.append(sprite)

    return sprites


async def sleep(tics=1):
    """Generate pause between frames"""

    for _ in range(int(tics)):
        await asyncio.sleep(0)
