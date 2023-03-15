from pathlib import Path
from nonebot import require, load_plugins

dir_ = Path(__file__).parent
require('nonebot_plugin_apscheduler')
load_plugins(str(dir_ / "xiuxian"))