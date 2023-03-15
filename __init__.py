from pathlib import Path
from nonebot import load_plugins

dir_ = Path(__file__).parent
load_plugins(str(dir_ / "nonebot_plugin_xiuxian_2.0"))