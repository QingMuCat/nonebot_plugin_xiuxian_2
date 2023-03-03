#!usr/bin/env python3
# -*- coding: utf-8 -*-
import random
from nonebot.rule import Rule
from nonebot import get_bots, get_bot
from enum import IntEnum, auto
from collections import defaultdict
from asyncio import get_running_loop
from typing import DefaultDict, Dict
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.adapters.onebot.v11.event import MessageEvent, GroupMessageEvent
from nonebot.adapters.onebot.v11 import Bot, MessageSegment
from .xiuxian_config import XiuConfig, JsonConfig
from .utils import get_msg_pic

_chat_flmt_notice = random.choice(
    ["慢...慢一..点❤，还有{}秒，让我在歇会！",
     "冷静一下，还有{}秒，让我在歇会！",
     "时间还没到，还有{}秒，歇会歇会~~"]
)


class CooldownIsolateLevel(IntEnum):
    """命令冷却的隔离级别"""

    GLOBAL = auto()
    """全局使用同一个冷却计时"""
    GROUP = auto()
    """群组内使用同一个冷却计时"""
    USER = auto()
    """按用户使用同一个冷却计时"""
    GROUP_USER = auto()
    """群组内每个用户使用同一个冷却计时"""


def Cooldown(
        cd_time: float = 0.1,
        at_sender: bool = False,
        isolate_level: CooldownIsolateLevel = CooldownIsolateLevel.USER,
        parallel: int = 5,
) -> None:
    """依赖注入形式的命令冷却

    用法:
        ```python
        @matcher.handle(parameterless=[Cooldown(cooldown=11.4514, ...)])
        async def handle_command(matcher: Matcher, message: Message):
            ...
        ```

    参数:
        cd_time: 命令冷却间隔
        at_sender: 是否at
        isolate_level: 命令冷却的隔离级别, 参考 `CooldownIsolateLevel`
        parallel: 并行执行的命令数量
    """
    if not isinstance(isolate_level, CooldownIsolateLevel):
        raise ValueError(
            f"invalid isolate level: {isolate_level!r}, "
            "isolate level must use provided enumerate value."
        )
    running: DefaultDict[str, int] = defaultdict(lambda: parallel)
    time_sy: Dict[str, int] = {}

    def increase(key: str, value: int = 1):
        running[key] += value
        if running[key] >= parallel:
            del running[key]
            del time_sy[key]
        return

    async def dependency(bot: Bot, matcher: Matcher, event: MessageEvent):
        loop = get_running_loop()

        if isolate_level is CooldownIsolateLevel.GROUP:
            key = str(
                event.group_id
                if isinstance(event, GroupMessageEvent)
                else event.user_id,
            )
        elif isolate_level is CooldownIsolateLevel.USER:
            key = str(event.user_id)
        elif isolate_level is CooldownIsolateLevel.GROUP_USER:
            key = (
                f"{event.group_id}_{event.user_id}"
                if isinstance(event, GroupMessageEvent)
                else str(event.user_id)
            )
        else:
            key = CooldownIsolateLevel.GLOBAL.name

        group_id = str(event.group_id)
        conf_data = JsonConfig().read_data()
        if group_id not in conf_data["group"]:
            if (
                    event.sender.role == "admin" or
                    event.sender.role == "owner" or
                    event.get_user_id() in bot.config.superusers
            ):

                await matcher.finish(message=f"本群已关闭修仙模组,请联系管理员开启,开启命令为【启用修仙功能】!", at_sender=True)
            else:
                await matcher.finish()
        else:
            pass
        if running[key] <= 0:
            if cd_time >= 1.5:
                time = int(cd_time - (loop.time() - time_sy[key]))
                if time <= 1:
                    time = 1
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + _chat_flmt_notice.format(time))
                    await matcher.finish(message=MessageSegment.image(pic))
                else:
                    await matcher.finish(message=_chat_flmt_notice.format(time), at_sender=at_sender)
            else:
                await matcher.finish()
        else:
            time_sy[key] = int(loop.time())
            running[key] -= 1
            loop.call_later(cd_time, lambda: increase(key))
        return

    return Depends(dependency)


put_bot = XiuConfig().put_bot
main_bot = XiuConfig().main_bo
layout_bot_dict = XiuConfig().layout_bot_dict


async def check_bot(bot: Bot) -> bool:  # 检测bot实例是否为主qq
    if str(bot.self_id) in put_bot:
        return True
    else:
        return False


def check_rule_bot() -> Rule:  # 对传入的消息检测，是主qq传入的消息就响应，其他的不响应
    async def _check_bot_(bot: Bot, event: GroupMessageEvent) -> bool:
        if str(bot.self_id) in put_bot:
            if str(event.get_user_id()) in main_bot:
                return False
            else:
                return True
        else:
            return False

    return Rule(_check_bot_)


async def range_bot(bot: Bot, event: GroupMessageEvent):  # 随机一个qq发送消息
    group_id = str(event.group_id)
    bot_list = list(get_bots().keys())
    try:
        bot = get_bots()[random.choice(bot_list)]
    except KeyError:
        pass
    return bot, group_id


async def assign_bot(bot: Bot, event: GroupMessageEvent):  # 按字典分配对应qq发送消息
    group_id = str(event.group_id)
    try:
        bot_id = layout_bot_dict[group_id]
        if type(bot_id) is str:
            bot = get_bots()[bot_id]
        elif type(bot_id) is list:
            bot = get_bots()[random.choice(bot_id)]
        else:
            bot = bot
    except:
        bot = bot
    return bot, group_id


async def assign_bot_group(group_id):  # 只导入群号，按字典分配对应qq发送消息
    group_id = str(group_id)
    try:
        bot_id = layout_bot_dict[group_id]
        if type(bot_id) is str:
            bot = get_bots()[bot_id]
        elif type(bot_id) is list:
            bot = get_bots()[random.choice(bot_id)]
        else:
            bot = get_bots()[put_bot[0]]
    except:
        bot = get_bot()
    return bot