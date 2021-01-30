import asyncio
import os

import aiofiles

from utils import get_streams, read_stream, write_log


async def start_chat_reader(host: str, port: int, log: str):
    """Start asyncio socket connection."""

    reader, writer = await get_streams(host, port)

    async with aiofiles.open(log, mode='a', buffering=1) as aiofile:

        while True:
            try:
                message = await read_stream(reader, writer, log=False)
                await write_log(aiofile, message)

            except (UnicodeDecodeError, AttributeError):
                pass

            except asyncio.CancelledError:
                writer.close()
                break

            except ConnectionError as ex:
                print(f'ConnectionError: {host}:{port}, {ex}')
                reader, writer = await get_streams(host, port)
                await asyncio.sleep(1)


if __name__ == '__main__':
    history_file = os.path.abspath(__file__ + '/../minechat.history')

    try:
        asyncio.run(start_chat_reader('minechat.dvmn.org', 5000, history_file))
    except (KeyboardInterrupt, SystemExit):
        print('\nManually closed')
