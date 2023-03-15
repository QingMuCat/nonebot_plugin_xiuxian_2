try:
    import ujson as json
except ImportError:
    import json
from pathlib import Path

DATABASE = Path() / "data" / "xiuxian"


class JsonDate:
    """处理基础配置 JSON数据"""

    def __init__(self):
        """基础配置 文件路径"""
        self.root_jsonpath = DATABASE / "灵根.json"
        self.level_rate_jsonpath = DATABASE / "突破概率.json"
        self.level_jsonpath = DATABASE / "境界.json"
        self.sect_json_pth = DATABASE / "宗门玩法配置.json"
        self.BACKGROUND_FILE = DATABASE / "image" / "background.png"
        self.BOSS_IMG = DATABASE / "boss_img" 
        self.BANNER_FILE = DATABASE / "image" / "banner.png"
        self.FONT_FILE = DATABASE / "font" / "sarasa-mono-sc-regular.ttf"

    def level_data(self):
        """境界数据"""
        with open(self.level_jsonpath, 'r', encoding='utf-8') as e:
            tp = e.read()
            data = json.loads(tp)
            return data

    def sect_config_data(self):
        """宗门玩法配置"""
        with open(self.sect_json_pth, "r", encoding="utf-8") as fp:
            file = fp.read()
            config_data = json.loads(file)
            return config_data

    def root_data(self):
        """获取灵根数据"""
        with open(self.root_jsonpath, 'r', encoding='utf-8') as e:
            file_data = e.read()
            data = json.loads(file_data)
            return data

    def level_rate_data(self):
        """获取境界突破概率"""
        with open(self.level_rate_jsonpath, 'r', encoding='utf-8') as e:
            file_data = e.read()
            data = json.loads(file_data)
            return data


jsondata = JsonDate()
