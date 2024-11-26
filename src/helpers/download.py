import asyncio
import logging
import mimetypes
import os
import uuid
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
import httpx

import config
from src.helpers.is_ import Is


async def download_file(
    url,
    tmp_path: Path = None,
    extension: str = ".png",
    max_retries: int = 5,
    get_bytes: bool = False,
):
    if not Is.url(url) and isinstance(url, Path) and url.exists():
        if get_bytes:
            with open(url, "rb") as f:
                return {
                    "mime": mimetypes.guess_type(url)[0],
                    "ext": url.suffix,
                    "bytes": f.read(),
                }
        else:
            return url

    extension = urlparse(url).path.split(".")[-1] if not extension else extension

    tmp_file_path = (tmp_path or config.TMP_PATH) / f"{uuid.uuid4().hex}.{extension}"

    def get_status_code(response):
        if hasattr(response, "status"):
            return response.status
        elif hasattr(response, "status_code"):
            return response.status_code
        return None

    async def fetch_with_session(session, client_get, retries, wait_time):
        while retries < max_retries:
            try:
                response = await client_get(session, url)

                status_code = get_status_code(response)

                if status_code == 200:
                    content_type = response.headers.get("content-type", "")
                    guess_ext = mimetypes.guess_extension(content_type)
                    if guess_ext == ".bin":
                        try:
                            guess_ext = os.path.splitext(urlparse(url).path)[1]
                        except Exception as e:
                            logging.warning(f"Error parsing URL extension: {e}")

                    ext = guess_ext or extension

                    if not ext.startswith("."):
                        ext = f".{ext}"

                    tmp_file_path_with_ext = tmp_file_path.with_suffix(ext)

                    file_bytes = await response.read()

                    if get_bytes:
                        return {
                            "mime": content_type,
                            "ext": tmp_file_path_with_ext.suffix,
                            "bytes": file_bytes,
                        }

                    with open(tmp_file_path_with_ext, "wb") as f:
                        f.write(file_bytes)

                    return tmp_file_path_with_ext
                elif status_code == 404:
                    logging.error(f"Failed to download {url} with status code 404")
                    return None
                else:
                    raise Exception(
                        f"Failed to download {url} with status code {status_code}"
                    )
            except Exception as e:
                retries += 1
                logging.error(f"Attempt {retries} failed to download {url}: {e}")
                logging.exception(e)
                await asyncio.sleep(wait_time)
                wait_time *= 2
        return None

    async def fetch_with_aiohttp():
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            return await fetch_with_session(
                session, lambda s, u: s.get(u), retries=0, wait_time=1
            )

    async def fetch_with_httpx():
        async with httpx.AsyncClient(timeout=120) as client:
            return await fetch_with_session(
                client, lambda s, u: s.get(u), retries=0, wait_time=1
            )

    result = await fetch_with_aiohttp()
    if not result:
        logging.info(f"Falling back to httpx for downloading {url}")
        result = await fetch_with_httpx()

    if not result:
        raise Exception(
            f"Failed to download {url} after {max_retries} attempts with both aiohttp and httpx"
        )

    return result
