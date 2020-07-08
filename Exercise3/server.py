import argparse
import asyncio
import os
import logging

import aiofiles
from aiohttp import web


async def get_chunks(proc: asyncio.subprocess, response: web.StreamResponse, size: int, delay: float) -> None:
    """Get chunks of archive and return to response."""
    chunk_count = 0
    download_complete = True
    try:
        while True:
            archive_chunk = await proc.stdout.read(n=1024 * size)

            if not archive_chunk:
                await response.write_eof()
                break

            chunk_count += 1
            logging.debug(f'Sending archive chunk {chunk_count}')
            await response.write(archive_chunk)
            await asyncio.sleep(delay)

    except asyncio.CancelledError:
        logging.debug('Download was interrupted')
        download_complete = False
        raise
    finally:
        if download_complete:
            logging.debug('Download Complete!')
        if proc.returncode:
            proc.kill()
            await proc.communicate()


async def archivate(request: web.Request) -> web.StreamResponse:
    """Archivate dir and stream response result."""
    serv_delay = request.app.get('serv_delay')
    serv_dir = request.app.get('serv_dir')
    serv_size = request.app.get('serv_size')
    archive_hash = request.match_info.get('archive_hash')
    full_path = f'{serv_dir}/{archive_hash}'
    path_exist = os.path.exists(f'{serv_dir}/{archive_hash}')

    if path_exist:
        cmd = f"zip -r - *"

        response = web.StreamResponse()
        response.headers['Content-Disposition'] = f'form-data; filename="photos.zip"'
        response.headers['Content-Type'] = 'application/zip'

        logging.debug("Started zipping:")
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE,
                                                     cwd=full_path)
        await response.prepare(request)
        await get_chunks(proc, response, serv_size, serv_delay)

        return response

    else:
        logging.debug(f'Archive or directory {full_path} not found')
        raise web.HTTPNotFound(text='Archive not found or deleted', content_type='text/html')


async def handle_index_page(request: web.Request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Microservice')
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser.add_argument("--log", action="store_true", help="On/off logging")
    parser.add_argument("--delay", type=float, default=0, help="Set delay for response")
    parser.add_argument("--dir", type=str, help="Set directory of photos", default="/tmp/photos")
    parser.add_argument("--port", type=int, default=8080, help="Set server port")
    parser.add_argument("--size", type=int, default=100, help="Set chunk size")
    args = parser.parse_args()

    app = web.Application()
    if str(os.getenv("SERV_LOG", args.log)) in ['1', 'True']:
        logging.basicConfig(format=u'[%(asctime)s] [%(filename)s] [LINE:%(lineno)d] %(message)s', level=logging.DEBUG)
    app['serv_delay'] = float(os.getenv("SERV_DELAY", args.delay))
    app['serv_dir'] = os.getenv("SERV_DIR", args.dir)
    app['serv_size'] = os.getenv("SERV_SIZE", args.size)

    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
    ])
    web.run_app(app, port=os.getenv("SERV_PORT", args.port))
