import configargparse
import asyncio
import os
import logging
from itertools import count

import aiofiles
from aiohttp import web


async def send_archive(proc: asyncio.subprocess, response: web.StreamResponse, size: int, delay: float) -> None:
    """Get chunks of archive and return to response."""
    download_complete = False
    try:
        for chunk_count in count(start=1):
            archive_chunk = await proc.stdout.read(n=1024 * size)

            if not archive_chunk:
                download_complete = True
                await response.write_eof()
                break

            logging.debug(f'Sending archive chunk {chunk_count}')
            await response.write(archive_chunk)
            await asyncio.sleep(delay)

    except asyncio.CancelledError:
        raise

    except BaseException:
        pass

    finally:
        if download_complete:
            logging.debug('Download Complete!')

        if proc.returncode != 0:
            logging.debug('Download was interrupted')
            proc.kill()

        await proc.communicate()


async def archivate(request: web.Request) -> web.StreamResponse:
    """Archivate dir and stream response result."""
    server_delay = request.app['server_delay']
    server_dir = request.app['server_dir']
    server_size = request.app['server_size']
    archive_hash = request.match_info['archive_hash']
    full_path = f'{server_dir}/{archive_hash}'
    path_exist = os.path.exists(f'{server_dir}/{archive_hash}')
    print(server_dir, full_path)
    cmd = ['zip', '-r', '-', archive_hash]

    if not path_exist:
        logging.debug(f'Archive or directory {full_path} not found')
        raise web.HTTPNotFound(text='Archive not found or deleted', content_type='text/html')

    response = web.StreamResponse()
    response.headers['Content-Disposition'] = f'form-data; filename="photos.zip"'
    response.headers['Content-Type'] = 'application/zip'

    logging.debug("Started zipping:")
    proc = await asyncio.create_subprocess_exec(*cmd,
                                                cwd=server_dir,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE,
                                                )
    await response.prepare(request)
    await send_archive(proc, response, server_size, server_delay)

    return response


async def handle_index_page(request: web.Request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    parser = configargparse.ArgParser()
    parser.add_argument("--log", action="store_true", default=False, help="On/off logging", env_var='SERVER_LOG')
    parser.add_argument("--delay", type=float, default=0, help="Set delay for response", env_var='SERVER_DELAY')
    parser.add_argument("--dir", help="Set directory of photos", default='/tmp/photos', env_var='SERVER_DIR')
    parser.add_argument("--port", type=int, default=8080, help="Set server port", env_var='SERVER_PORT')
    parser.add_argument("--size", type=int, default=100, help="Set chunk size in KB")
    options = parser.parse_args()

    app = web.Application()

    if options.log:
        logging.basicConfig(format=u'[%(asctime)s] [%(filename)s] [LINE:%(lineno)d] %(message)s', level=logging.DEBUG)

    app['server_delay'] = options.delay
    app['server_dir'] = options.dir
    app['server_size'] = options.size

    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
    ])
    web.run_app(app, port=options.port)
