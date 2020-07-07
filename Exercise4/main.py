import argparse
import asyncio
from typing import Union
import os

from chat_reader import start_chat_reader
from chat_writer import start_chat_writer


async def main(host: str, port: int, log: str, key: Union[str, None]):

    await asyncio.gather(
        start_chat_reader(host, port, log),
        start_chat_writer(host, 5050, key)
    )


if __name__ == '__main__':
    current_dir = os.getcwd()
    full_path = f'{current_dir}/chat.log'
    parser = argparse.ArgumentParser(prog='Chat connector')
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser.add_argument("--host", type=str, default='minechat.dvmn.org', help="Set server host")
    parser.add_argument("--port", type=int, default=5000, help="Set server port")
    parser.add_argument("--log", type=str, default=full_path, help="Path to log file")
    parser.add_argument("--key", type=str, help="Set user hash key")
    args = parser.parse_args()

    server_host = os.getenv("SERV_HOST", args.host)
    server_port = int(os.getenv("SERV_PORT", args.port))
    server_log = os.getenv("SERV_LOG", args.log)
    serv_key = os.getenv("SERV_KEY", args.key)

    try:
        asyncio.run(main(server_host, server_port, server_log, serv_key))
    except KeyboardInterrupt:
        print('Manually closed')
