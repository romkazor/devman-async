import asyncio
import logging
from asyncio import StreamReader, StreamWriter
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Tuple


logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_streams(host: str, port: int) -> AsyncGenerator[Tuple[StreamReader, StreamWriter], None]:
    """Open connection and get objects: StreamReader and StreamWriter."""

    reconnect_counter = 0
    server = f'{host}:{port}'

    while True:
        writer = None

        try:
            logger.info(f'Connecting to server {server} ...')
            reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=2)
            logger.info(f'Connection established to {server}')
            yield reader, writer

        except asyncio.TimeoutError:
            logger.exception(f'TimeoutError -> {server}', exc_info=False)
        except ConnectionError as ex:
            logger.exception(f'ConnectionError -> {server}, {ex.__class__.__name__}: {ex}', exc_info=False)
        except Exception as ex:
            logger.exception(f'OtherError -> {server}, {ex.__class__.__name__}: {ex}', exc_info=False)

        finally:
            if writer:
                writer.close()
                break
            reconnect_counter += 1
            await asyncio.sleep(60 if reconnect_counter > 60 else reconnect_counter)


async def read_stream(reader: StreamReader, writer: StreamWriter, log: bool = True) -> AsyncGenerator[str, None]:
    """Reading line from stream."""

    reconnect_counter = 0

    try:
        while not reader.at_eof():
            data = await asyncio.wait_for(reader.readline(), timeout=60)
            message = data.decode('utf-8').strip()
            if log:
                logger.debug(message)
            yield message

    except asyncio.TimeoutError:
        logger.exception(f'TimeoutError -> StreamReader timeout get message', exc_info=False)
    except Exception as ex:
        logger.exception(f'OtherError -> {ex.__class__.__name__}: {ex}', exc_info=False)

    finally:
        reconnect_counter += 1
        await asyncio.sleep(60 if reconnect_counter > 60 else reconnect_counter)
