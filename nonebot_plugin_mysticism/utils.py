from io import BytesIO
import os
import aiohttp
import hashlib
import tempfile
import pathlib


# 返回BytesIO对象图片
async def send_image_as_bytes(url: str, cache: bool = True):
    path = pathlib.Path(tempfile.gettempdir()) / "tarot"
    if not os.path.exists(path):
        os.mkdir(path)
    path /= hashlib.sha256(url.encode()).hexdigest()

    if os.path.exists(path):
        with open(path, mode="rb") as f:
            buffered = BytesIO(f.read())
            buffered.seek(0)
            return buffered

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                with open(path, mode="wb+") as f:
                    f.write(image_data)
                buffered = BytesIO(image_data)
                buffered.seek(0)
                return buffered
            else:
                return None
