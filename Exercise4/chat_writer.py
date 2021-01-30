import asyncio
import json
import os
from contextlib import suppress
from json.decoder import JSONDecodeError
from typing import Optional

import aiofiles
import configargparse

from utils import get_streams, logger, read_stream


HELLO_USER_MSG = 'Hello %username%! Enter your personal hash or leave it empty to create new account.'
WELCOME_MSG = 'Welcome to chat! Post your message below. End it with an empty line.'
SEND_MSG = 'Message send. Write more, end message with an empty line.'


async def authorise(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, token: str) -> bool:
    """Authorise user."""

    try:
        message = await read_stream(reader)

        if message == HELLO_USER_MSG:
            writer.write(f'{token}\n'.encode())
            await writer.drain()

            message = await read_stream(reader)
            with suppress(JSONDecodeError):
                message = json.loads(message)
                if message:
                    logger.debug(f'Successfully authorised: {message["nickname"]}')
                    return True

        logger.debug('Unknown token. Please check or try register again.')
        return False

    except asyncio.CancelledError:
        writer.close()


async def register(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, chat_username: Optional[str]) -> str:
    """Register new user."""

    key = ''

    try:
        message = await read_stream(reader)

        if message == HELLO_USER_MSG:
            writer.write(f'\n'.encode())
            await writer.drain()

            message = await read_stream(reader)
            if message == 'Enter preferred nickname below:':
                if not chat_username:
                    chat_username = input(message + ' ').replace('\\n', '').replace('\n', '')
                writer.write(f'{chat_username}\n\n'.encode())
                await writer.drain()

                message = await read_stream(reader)
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
        message = await read_stream(reader)

        if message == WELCOME_MSG:
            if chat_message:
                chat_message = chat_message.replace('\\n', '').replace('\n', '')
            else:
                chat_message = input('Enter message ')
                chat_message = chat_message.replace('\\n', '').replace('\n', '')
            writer.write(f'{chat_message}\n\n'.encode())
            await writer.drain()

            await read_stream(reader)

    except asyncio.CancelledError:
        writer.close()


async def start_chat_writer(host: str, port: int, token: str, do_register: bool,
                            chat_username: Optional[str], chat_message: Optional[str]):
    """Start asyncio socket connection."""

    reader, writer = await get_streams(host, port)

    try:
        if do_register:
            token = await register(reader, writer, chat_username)
            writer.close()

        await authorise(reader, writer, token)
        await submit_message(reader, writer, chat_message)

        writer.close()

    except asyncio.CancelledError:
        writer.close()


if __name__ == '__main__':
    logger.name = 'chat_writer'
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

    chat_host = options.host
    chat_port = options.port
    chat_key = options.key
    chat_register = options.register
    chat_username = options.username
    chat_message = options.message

    if chat_username and not chat_register:
        parser.error('--register required when --username is used.')

    try:
        asyncio.run(start_chat_writer(chat_host, chat_port, chat_key, chat_register, chat_username, chat_message))
    except (KeyboardInterrupt, SystemExit):
        print('\nManually closed')
