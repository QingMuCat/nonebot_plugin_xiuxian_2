import httpx
from nonebot.log import logger
import asyncio
import hashlib
import os
from PIL import Image
import io
from pathlib import Path


async def download_url(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=20)
                resp.raise_for_status()
                return resp.content
            except Exception as e:
                logger.warning(f"Error downloading {url}, retry {i}/3: {e}")
                await asyncio.sleep(3)
    raise Exception(f"{url} 下载失败！")


async def download_avatar(user_id: str) -> bytes:
    url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    data = await download_url(url)
    if hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
        url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
        data = await download_url(url)
    return data


async def get_avatar_by_user_id_and_save(user_id):
    user_id = str(user_id)
    PLAYERSDATA = Path() / "data" / "xiuxian" / "players"
    USER_AVATAR_PATH = PLAYERSDATA / user_id / 'AVATAR.png'
    INIT_PATH = Path() / "data" / "xiuxian" / "info_img" / "init.png"

    try:
        logger.info("开始下载用户头像！")
        image_bytes = await download_avatar(user_id)
        im = Image.open(io.BytesIO(image_bytes)).resize((280, 280)).convert("RGBA")
        if not os.path.exists(PLAYERSDATA / user_id):  # 用户文件夹不存在
            os.makedirs(PLAYERSDATA / user_id)
        im.save(USER_AVATAR_PATH, "PNG")
    except Exception as e:
        logger.error(f"获取头像出错,{e}")
        im = Image.open(INIT_PATH).resize((280, 280)).convert("RGBA")
    return im


