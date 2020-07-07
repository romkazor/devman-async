import asyncio
from datetime import datetime

import aiofiles
from aiofiles.threadpool.text import AsyncTextIOWrapper
from async_timeout import timeout


async def write_log(aiofile: AsyncTextIOWrapper, message: str) -> None:
    """Write log to specific file with datetime"""
    now = datetime.now().strftime("%d.%m.%y %H:%M")
    await aiofile.write(f'[{now}] {message}\n')


async def get_streams(host: str, port: int) -> (asyncio.StreamReader, asyncio.StreamWriter):
    """Open connection and get objects: StreamReader and StreamWriter"""
    reader, writer = None, None
    try:
        async with timeout(1.5):
            reader, writer = await asyncio.open_connection(host, port)
            message = f'Connection established to {host}:{port}'
            print(message)
    except asyncio.TimeoutError:
        print(f'Timeout connection to {host}:{port}')
    finally:
        return reader, writer


async def start_chat_reader(host: str, port: int, log: str):
    """Start asyncio socket connection"""
    reader, writer = await get_streams(host, port)

    if reader and writer:
        async with aiofiles.open(log, mode='a', buffering=1) as aiofile:

            while True:
                try:
                    data = await reader.readline()
                    message = data.decode('utf-8').strip()
                    print(message)
                    await write_log(aiofile, message)

                except asyncio.CancelledError:
                    writer.close()
                    break

                except UnicodeDecodeError:
                    pass
