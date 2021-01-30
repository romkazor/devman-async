import asyncio
import logging.handlers
import os
from asyncio import StreamReader, StreamWriter
from datetime import datetime
from socket import gaierror
from typing import Tuple, Union

from aiofiles.threadpool.binary import AsyncBufferedIOBase
from aiofiles.threadpool.text import AsyncTextIOWrapper


logging.basicConfig(level=logging.DEBUG,
                    handlers=[
                        logging.handlers.WatchedFileHandler(os.path.abspath(__file__ + '/../chat.log')),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def write_log(aiofile: Union[AsyncTextIOWrapper, AsyncBufferedIOBase], message: str) -> None:
    """Write log to specific file with datetime."""

    now = datetime.now().strftime("%d.%m.%y %H:%M")
    print(message)
    await aiofile.write(f'[{now}] {message}\n')


async def get_streams(host: str, port: int) -> Tuple[StreamReader, StreamWriter]:
    """Open connection and get objects: StreamReader and StreamWriter."""

    while True:
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=1.5)
            print(f'Connection established to {host}:{port}')
            return reader, writer

        except TimeoutError:
            print(f'Timeout connection to {host}:{port}')
            await asyncio.sleep(1)

        except (ConnectionError, gaierror) as ex:
            print(f'ConnectionError: {host}:{port}, {ex}')
            await asyncio.sleep(1)


async def read_stream(reader: StreamReader, log: bool = True) -> str:
    """Reading line from stream."""

    try:
        data = await reader.readline()
        message = data.decode('utf-8').strip()
        if log:
            logger.debug(message)

        return message

    except UnicodeDecodeError:
        message = 'null'
        logger.debug(message)
        return message

    except asyncio.CancelledError:
        raise asyncio.CancelledError
