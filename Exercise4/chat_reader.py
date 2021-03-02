import asyncio
import configargparse
import logging.handlers
import os

import aiofiles

from stream_helpers import get_streams, read_stream
from log_helper import write_log


logger = logging.getLogger(__name__)


async def start_chat_reader(host: str, port: int, log: str):
    """Start asyncio socket connection."""

    server = f'{host}:{port}'

    while True:
        try:
            async with aiofiles.open(log, mode='a', buffering=1) as aiofile:
                async with get_streams(host, port) as (reader, writer):
                    async for message in read_stream(reader, writer, log=False):
                        await write_log(aiofile, message)
        except RuntimeError as ex:
            logger.exception(f'RuntimeError -> {server}, {ex}', exc_info=False)
            break
        except Exception as ex:
            logger.exception(f'OtherError -> {server}, {ex.__class__.__name__}: {ex}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING,
                        format="[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                        handlers=[
                            logging.handlers.WatchedFileHandler(os.path.abspath(__file__ + '/../chat.log')),
                            logging.StreamHandler()
                        ])
    logger.setLevel(logging.DEBUG)
    logging.getLogger('stream_helpers').setLevel(logging.DEBUG)

    history_file = os.path.abspath(__file__ + '/../minechat.history')

    parser = configargparse.ArgParser()
    parser.add_argument("--host", type=str, default='minechat.dvmn.org', help="Set server host", env_var='CHAT_HOST')
    parser.add_argument("--port", type=int, default=5000, help="Set server port", env_var='CHAT_PORT')
    parser.add_argument("--history", type=str, default=history_file, help='Path to log file', env_var='CHAT_HISTORY')
    options = parser.parse_args()

    try:
        asyncio.run(start_chat_reader(options.host, options.port, options.history))
    except (KeyboardInterrupt, SystemExit):
        print('\nManually closed')
