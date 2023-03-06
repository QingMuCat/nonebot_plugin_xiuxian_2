import os
import zipfile
import wget
from pathlib import Path
from nonebot.log import logger
from .xiuxian_config import XiuConfig


def download_xiuxian_data():
    path_data = Path() / "data"
    zipPath = str(path_data / "xiuxian_data_temp.zip")  # 压缩包的绝对路径
    version = "xiuxian_version.txt"
    URL = "https://huggingface.co/xiaonana/xiuxian/resolve/main/xiuxian.zip"

    def get_data():
        wget.download(URL, out=zipPath)  # 获取内容

    def _main_():
        if not os.path.exists(path_data):
            os.makedirs(path_data)
        version_path = path_data / "xiuxian" / version
        data = None
        try:
            with open(version_path, 'r', encoding='utf-8') as f:
                data = f.read()
                f.close()
        except:
            pass
        if str(data) == str(XiuConfig().version):
            logger.info("修仙配置校核完成！")
        else:
            logger.info("正在更新修仙配置文件，请等待！")
            try:
                get_data()  # data为byte字节
                logger.info(f"正在解压修仙配置文件！")
                with zipfile.ZipFile(file=zipPath, mode='r') as zf:
                    for old_name in zf.namelist():
                        # 获取文件大小，目的是区分文件夹还是文件，如果是空文件应该不好用。
                        file_size = zf.getinfo(old_name).file_size
                        new_name = old_name.encode('cp437').decode('gbk')
                        new_path = os.path.join(path_data, new_name)
                        if file_size > 0:
                            with open(file=new_path, mode='wb') as f:
                                f.write(zf.read(old_name))
                                f.close()
                        else:
                            if not os.path.exists(new_path):
                                os.makedirs(new_path)
                zf.close()
            except Exception as e:
                logger.info(f"修仙配置文件下载失败，原因{e}，一直失败请前往网址手动下载{URL}")
            finally:
                try:
                    os.remove(zipPath)
                    logger.info(f"原始压缩包已删除！")
                except:
                    logger.info(f"原始压缩包删除失败，请手动删除，路径{zipPath}!")
    return _main_()
