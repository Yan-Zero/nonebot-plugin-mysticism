from io import BytesIO
import aiohttp


# 返回BytesIO对象图片
async def send_image_as_bytes(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                buffered = BytesIO(image_data)
                buffered.seek(0)
                return buffered
            else:
                return None
