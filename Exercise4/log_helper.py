import logging
from datetime import datetime
from typing import Union

from aiofiles.threadpool.binary import AsyncBufferedIOBase
from aiofiles.threadpool.text import AsyncTextIOWrapper

logger = logging.getLogger(__name__)


async def write_log(aiofile: Union[AsyncTextIOWrapper, AsyncBufferedIOBase], message: str) -> None:
    """Write log to specific file with datetime."""

    now = datetime.now().strftime("%d.%m.%y %H:%M")
    print(message)
    await aiofile.write(f'[{now}] {message}\n')
