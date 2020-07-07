import asyncio

from chat_reader import get_streams


async def start_chat_writer(host: str, port: int, token: str):
    """Start asyncio socket connection"""
    await asyncio.sleep(0.5)
    reader, writer = await get_streams(host, port)

    if reader and writer:

        while True:
            try:
                data = await reader.readline()
                message = data.decode('utf-8').strip()

                if message.startswith('Hello'):
                    print(message)
                    writer.write(f'{token}\n'.encode())

                elif message.startswith('Welcome'):
                    print(message)
                    writer.write(f'Hello guys!!!\n\n'.encode())

                else:
                    print(message)

            except asyncio.CancelledError:
                writer.close()
                break

            except UnicodeDecodeError:
                pass
