#!usr/bin/env python3
# -*- coding: utf-8 -*-
import nonebot
from nonebot import require, get_driver
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from nonebot.message import event_preprocessor, IgnoredException
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

from pathlib import Path
from pkgutil import iter_modules

from .download_xiuxian_data import download_xiuxian_data
from .xiuxian_config import XiuConfig
from .config import config as _config


DRIVER = get_driver()

try:
    NICKNAME: str = list(DRIVER.config.nickname)[0]
except Exception as e:
    logger.info(f"缺少超级用户配置文件，{e}!")
    NICKNAME = "bot"

try:
    download_xiuxian_data()
except Exception as e:
    logger.info(f"下载配置文件失败，修仙插件无法加载，{e}!")
    raise ImportError

put_bot = XiuConfig().put_bot
shield_group = XiuConfig().shield_group

try:
    put_bot_ = put_bot[0]
except:
    logger.info(f"修仙插件没有配置put_bot,如果有多个qq和nb链接,请务必配置put_bot,具体介绍参考【风控帮助】！")

require("nonebot_plugin_apscheduler")

nonebot.load_plugins(str(Path(__file__).parent.resolve()))

__plugin_meta__ = PluginMetadata(
    name="修仙模拟器",
    description="修仙游戏",
    usage=("必死之境机逢仙缘，修仙之路波澜壮阔！\n" " 输入 < /修仙帮助 > 获取仙界信息"),
    extra={"show": True, "priority": 15},
)


@event_preprocessor
async def do_something(bot: Bot, event: GroupMessageEvent):
    global put_bot
    if not put_bot:
        pass
    else:
        if str(bot.self_id) in put_bot:
            if str(event.group_id) in shield_group:
                raise IgnoredException("为屏蔽群消息,已忽略")
            else:
                pass
        else:
            raise IgnoredException("非主bot信息,已忽略")
