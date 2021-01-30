import asyncio
import configargparse
import os

import aiofiles

from utils import get_streams, read_stream, write_log


async def start_chat_reader(host: str, port: int, log: str):
    """Start asyncio socket connection."""

    reader, writer = await get_streams(host, port)

    async with aiofiles.open(log, mode='a', buffering=1) as aiofile:

        while True:
            try:
                message = await read_stream(reader, log=False)
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

    parser = configargparse.ArgParser()
    parser.add_argument("--host", type=str, default='minechat.dvmn.org', help="Set server host", env_var='CHAT_HOST')
    parser.add_argument("--port", type=int, default=5000, help="Set server port", env_var='CHAT_PORT')
    parser.add_argument("--history", type=str, default=history_file, help='Path to log file', env_var='CHAT_HISTORY')
    options = parser.parse_args()

    chat_host = options.host
    chat_port = options.port
    chat_history = options.history

    try:
        asyncio.run(start_chat_reader(chat_host, chat_port, chat_history))
    except (KeyboardInterrupt, SystemExit):
        print('\nManually closed')
