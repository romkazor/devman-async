import asyncio
import json
import logging.handlers
import os
from contextlib import suppress
from json.decoder import JSONDecodeError
from typing import Optional

import aiofiles
import configargparse

from stream_helpers import get_streams, read_stream


logger = logging.getLogger(__name__)

HELLO_USER_MSG = 'Hello %username%! Enter your personal hash or leave it empty to create new account.'
WELCOME_MSG = 'Welcome to chat! Post your message below. End it with an empty line.'
SEND_MSG = 'Message send. Write more, end message with an empty line.'
NICKNAME_MSG = 'Enter preferred nickname below:'


async def authorise(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, token: str) -> bool:
    """Authorise user."""

    async for message in read_stream(reader, writer, log=False):

        if message == HELLO_USER_MSG:
            print(message)
            writer.write(f'{token}\n'.encode())
            await writer.drain()

            data = await reader.readline()
            message = data.decode('utf-8').strip()
            with suppress(JSONDecodeError):
                message = json.loads(message)
                if message:
                    logger.debug(f'Successfully authorised: {message["nickname"]}')
                    return True

        logger.debug('Unknown token. Please check or try register again.')
        return False


async def register(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, chat_username: Optional[str]) -> str:
    """Register new user."""

    key = ''

    try:
        async for message in read_stream(reader, writer, log=False):
            if message == HELLO_USER_MSG:
                writer.write(f'\n'.encode())
                await writer.drain()

                data = await reader.readline()
                message = data.decode('utf-8').strip()
                if message == NICKNAME_MSG:
                    if not chat_username:
                        chat_username = input(message + ' ').replace('\\n', '').replace('\n', '')
                    writer.write(f'{chat_username}\n\n'.encode())
                    await writer.drain()

                    data = await reader.readline()
                    message = data.decode('utf-8').strip()
                    with suppress(JSONDecodeError):
                        token = json.loads(message)
                        if token:
                            key = token['account_hash']
                            key_file = os.path.abspath(__file__ + '/../key')
                            async with aiofiles.open(key_file, mode='w', buffering=1) as aiofile:
                                await aiofile.write(key)

            return key

    except asyncio.CancelledError:
        writer.close()


async def submit_message(reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                         chat_message: Optional[str] = None):
    """Send message."""

    try:
        async for message in read_stream(reader, writer, log=False):

            if message == WELCOME_MSG:
                if chat_message:
                    chat_message = chat_message.replace('\\n', '').replace('\n', '')
                else:
                    chat_message = input('Enter message ')
                    chat_message = chat_message.replace('\\n', '').replace('\n', '')

                writer.write(f'{chat_message}\n\n'.encode())
                await writer.drain()

                data = await reader.readline()
                message = data.decode('utf-8').strip()
                print(message)
            return

    except asyncio.CancelledError:
        writer.close()


async def start_chat_writer(host: str, port: int, token: str, do_register: bool,
                            chat_username: Optional[str], chat_message: Optional[str]):
    """Start asyncio socket connection."""

    server = f'{host}:{port}'

    try:
        async with get_streams(host, port) as (reader, writer):

            if do_register:
                token = await register(reader, writer, chat_username)
                writer.close()

            await authorise(reader, writer, token)
            await submit_message(reader, writer, chat_message)

    except RuntimeError as ex:
        logger.exception(f'RuntimeError -> {server}, {ex}', exc_info=False)
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

    key_file = os.path.abspath(__file__ + '/../key')
    key = None

    with suppress(FileNotFoundError):
        with open(key_file) as file:
            key = file.readline()

    parser = configargparse.ArgParser()
    parser.add_argument("--host", type=str, default='minechat.dvmn.org', help="Set server host", env_var='ACHAT_HOST')
    parser.add_argument("--port", type=int, default=5050, help="Set server port", env_var='ACHAT_PORT')
    parser.add_argument("--key", type=str, default=key, help='Set user hash key', env_var='ACHAT_KEY')
    parser.add_argument("--register", help='Register new user', action='store_true', default=False, env_var='ACHAT_REGISTER')
    parser.add_argument("--username", type=str, help='Set username for register. --register required', env_var='ACHAT_USERNAME')
    parser.add_argument("--message", type=str, required=True, help='Message for chat', env_var='ACHAT_MESSAGE')
    options = parser.parse_args()

    if options.username and not options.register:
        parser.error('--register required when --username is used.')

    try:
        asyncio.run(start_chat_writer(options.host, options.port, options.key, options.register,
                                      options.username, options.message))
    except (KeyboardInterrupt, SystemExit):
        print('\nManually closed')
