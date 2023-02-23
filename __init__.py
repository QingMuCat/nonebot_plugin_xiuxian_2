#!usr/bin/env python3
# -*- coding: utf-8 -*-
from .download_xiuxian_data import download_xiuxian_data
from nonebot.plugin import PluginMetadata
from nonebot import load_all_plugins
from nonebot import get_bot
from nonebot.log import logger
from nonebot.message import event_preprocessor, IgnoredException
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent
)
from nonebot import get_driver
from .xiuxian_config import XiuConfig

DRIVER = get_driver()

try:
    NICKNAME: str = list(DRIVER.config.nickname)[0]
except Exception as e:
    logger.info(f"缺少超级用户配置文件，{e}！")
    NICKNAME = 'bot'

try:
    download_xiuxian_data()
except Exception as e:
    logger.info(f"缺少配置文件，修仙插件无法加载，{e}！")
    raise ImportError

put_bot = XiuConfig().put_bot
shield_group = XiuConfig().shield_group

src = ''
load_all_plugins(
    [
        f'{src}nonebot_plugin_xiuxian_2.xiuxian_base',
        f'{src}nonebot_plugin_xiuxian_2.xiuxian_boss',
        f'{src}nonebot_plugin_xiuxian_2.xiuxian_bank',
        f'{src}nonebot_plugin_xiuxian_2.xiuxian_sect',
        f'{src}nonebot_plugin_xiuxian_2.xiuxian_info',
        f'{src}nonebot_plugin_xiuxian_2.xiuxian_buff',
        f'{src}nonebot_plugin_xiuxian_2.xiuxian_back',
        f'{src}nonebot_plugin_xiuxian_2.xiuxian_rift',
        f'{src}nonebot_plugin_xiuxian_2.xiuxian_mixelixir',
        f'{src}nonebot_plugin_xiuxian_2.xiuxian_work',
        f'{src}nonebot_plugin_xiuxian_2.xiuxian_impart',
        f'{src}nonebot_plugin_xiuxian_2.xiuxian_impart_pk',
    ],
    [],
)

__plugin_meta__ = PluginMetadata(
    name='修仙模拟器',
    description='',
    usage=(
        "必死之境机逢仙缘，修仙之路波澜壮阔！\n"
        " 输入 < 修仙帮助 > 获取仙界信息"
    ),
    extra={
        "show": True,
        "priority": 15
    }
)


@DRIVER.on_startup
async def put_bot_():
    global put_bot
    if put_bot is []:
        put_bot = put_bot.append(str(get_bot().self_id))
        logger.info(f"修仙插件没有配置put_bot，已自动配置{put_bot}")


@event_preprocessor
async def do_something(bot: Bot, event: GroupMessageEvent):
    if not put_bot:
        pass
    else:
        if str(bot.self_id) in put_bot:
            if str(event.group_id) in shield_group:
                raise IgnoredException("为屏蔽群消息，已忽略")
            else:
                pass
        else:
            raise IgnoredException("非主bot信息，已忽略")
