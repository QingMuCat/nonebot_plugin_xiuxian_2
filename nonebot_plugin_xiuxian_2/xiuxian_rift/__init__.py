import random
from datetime import datetime
from nonebot import get_bots, on_command, require, on_fullmatch
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    GROUP,
    Message,
    GroupMessageEvent,
    GROUP_ADMIN,
    GROUP_OWNER,
    MessageSegment
)
from .old_rift_info import old_rift_info
from .. import DRIVER
from ..lay_out import assign_bot, assign_bot_group, put_bot, Cooldown
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from ..xiuxian2_handle import XiuxianDateManage
from ..utils import (
    check_user, check_user_type,
    send_forward_msg_list, get_msg_pic, CommandObjectID
)
from .riftconfig import get_config, savef
from .jsondata import save_rift_data, read_rift_data
from ..xiuxian_config import XiuConfig
from .riftmake import (
    Rift, get_rift_type, get_story_type, NONEMSG, get_battle_type,
    get_dxsj_info, get_boss_battle_info, get_treasure_info
)


config = get_config()
sql_message = XiuxianDateManage()  # sql类
cache_help = {}
group_rift = {}  # dict
groups = config['open']  # list
# 定时任务
set_rift = require("nonebot_plugin_apscheduler").scheduler

set_group_rift = on_command("群秘境", priority=4, permission=GROUP and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER), block=True)
explore_rift = on_fullmatch("探索秘境", priority=5, permission=GROUP, block=True)
rift_help = on_fullmatch("秘境帮助", priority=6, permission=GROUP, block=True)
create_rift = on_fullmatch("生成秘境", priority=5, permission=GROUP and SUPERUSER, block=True)
complete_rift = on_command("秘境结算", aliases={"结算秘境"}, priority=7, permission=GROUP, block=True)
break_rift = on_command("秘境探索终止", aliases={"终止探索秘境"}, priority=7, permission=GROUP, block=True)

__rift_help__ = f"""
秘境帮助信息:
指令：
1、群秘境开启、关闭:开启本群的秘境生成，管理员权限
2、生成秘境:生成一个随机秘境，超管权限
3、探索秘境:探索秘境获取随机奖励
4、秘境结算、结算秘境:结算秘境奖励
5、秘境探索终止、终止探索秘境:终止秘境事件
6、秘境帮助:获取秘境帮助信息
非指令：
1、每日18点30分生成一个随机等级的秘境
""".strip()


@DRIVER.on_startup
async def read_rift_():
    global group_rift
    group_rift.update(old_rift_info.read_rift_info())
    logger.info("历史rift数据读取成功")


@DRIVER.on_shutdown
async def save_rift_():
    global group_rift
    old_rift_info.save_rift(group_rift)
    logger.info("rift数据已保存")


# 定时任务生成群秘境
@set_rift.scheduled_job("cron", hour=18, minute=30)
async def set_rift_():
    global group_rift
    # bot = get_bots()[put_bot[0]]
    if groups:
        group_rift = {}
        for group_id in groups:
            bot = await assign_bot_group(group_id=group_id)
            rift = Rift()
            rift.name = get_rift_type()
            rift.rank = config['rift'][rift.name]['rank']
            rift.count = config['rift'][rift.name]['count']
            rift.time = config['rift'][rift.name]['time']
            group_rift[group_id] = rift
            msg = f"秘境已刷新，野生的{rift.name}已开启！可探索次数：{rift.count}次，请诸位道友发送 探索秘境 来加入吧！"
            pic = await get_msg_pic(msg)  #
            await bot.send_group_msg(group_id=int(group_id), message=MessageSegment.image(pic))


@rift_help.handle(parameterless=[Cooldown(at_sender=True)])
async def rift_help_(bot: Bot, event: GroupMessageEvent, session_id: int = CommandObjectID()):
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    if session_id in cache_help:
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(cache_help[session_id]))
        await rift_help.finish()
    else:
        msg = __rift_help__
        if XiuConfig().img:
            pic = await get_msg_pic(msg, scale=False)
            cache_help[session_id] = pic
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await rift_help.finish()


# 生成秘境
@create_rift.handle(parameterless=[Cooldown(at_sender=True)])
async def create_rift_(bot: Bot, event: GroupMessageEvent):
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    group_id = str(event.group_id)
    if group_id not in groups:
        msg = '本群尚未开启秘境，请联系管理员开启群秘境'
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await create_rift.finish()

    try:
        var = group_rift[group_id]
        msg = f"当前已存在{group_rift[group_id].name}，秘境可探索次数：{group_rift[group_id].count}次，请诸位道友发送 探索秘境 来加入吧！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await create_rift.finish()
    except KeyError:
        rift = Rift()
        rift.name = get_rift_type()
        rift.rank = config['rift'][rift.name]['rank']
        rift.count = config['rift'][rift.name]['count']
        rift.time = config['rift'][rift.name]['time']
        group_rift[group_id] = rift
        msg = f"野生的{rift.name}出现了！秘境可探索次数：{rift.count}次，请诸位道友发送 探索秘境 来加入吧！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await create_rift.finish()


# 探索秘境
@explore_rift.handle(parameterless=[Cooldown(at_sender=True)])
async def _(bot: Bot, event: GroupMessageEvent):
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await explore_rift.finish()

    user_id = user_info.user_id
    is_type, msg = check_user_type(user_id, 0)  # 需要无状态的用户
    if not is_type:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await explore_rift.finish()
    else:
        group_id = str(event.group_id)
        if group_id not in groups:
            msg = '本群尚未开启秘境，请联系管理员开启群秘境'
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await explore_rift.finish()
        try:
            group_rift[group_id]
        except:
            msg = '野外秘境尚未生成，请道友耐心等待!'
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await explore_rift.finish()
        if user_id in group_rift[group_id].l_user_id:
            msg = '道友已经参加过本次秘境啦，请把机会留给更多的道友！'
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await explore_rift.finish()

        group_rift[group_id].l_user_id.append(user_id)
        group_rift[group_id].count -= 1
        msg = f"道友进入秘境：{group_rift[group_id].name}，探索需要花费时间：{group_rift[group_id].time}分钟！"
        rift_data = {
            "name": group_rift[group_id].name,
            "time": group_rift[group_id].time,
            "rank": group_rift[group_id].rank
        }

        save_rift_data(user_id, rift_data)
        sql_message.do_work(user_id, 3, rift_data["time"])
        if group_rift[group_id].count == 0:
            del group_rift[group_id]
            logger.info('群{group_id}秘境已到上限次数！')
            msg += "秘境随着道友的进入，已无法再维持更多的人，而关闭了！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await explore_rift.finish()
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await explore_rift.finish()


# 结算秘境
@complete_rift.handle(parameterless=[Cooldown(at_sender=True)])
async def complete_rift_(bot: Bot, event: GroupMessageEvent):
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await complete_rift.finish()

    user_id = user_info.user_id

    group_id = str(event.group_id)
    if group_id not in groups:
        msg = '本群尚未开启秘境，请联系管理员开启群秘境'
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await complete_rift.finish()

    is_type, msg = check_user_type(user_id, 3)  # 需要在秘境的用户
    if not is_type:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await complete_rift.finish()
    else:
        rift_info = None
        try:
            rift_info = read_rift_data(user_id)
        except:
            msg = '发生未知错误！'
            sql_message.do_work(user_id, 0)
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await complete_rift.finish()

        user_cd_message = sql_message.get_user_cd(user_id)
        work_time = datetime.strptime(
            user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
        )
        exp_time = (datetime.now() - work_time).seconds // 60  # 时长计算
        time2 = rift_info["time"]
        if exp_time < time2:
            msg = f"进行中的：{rift_info['name']}探索，预计{time2 - exp_time}分钟后可结束"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await complete_rift.finish()
        else:  # 秘境结算逻辑
            sql_message.do_work(user_id, 0)
            rift_rank = rift_info["rank"]  # 秘境等级
            rift_type = get_story_type()  # 无事、宝物、战斗
            if rift_type == "无事":
                msg = random.choice(NONEMSG)
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await complete_rift.finish()
            elif rift_type == "战斗":
                rift_type = get_battle_type()
                if rift_type == "掉血事件":
                    msg = get_dxsj_info("掉血事件", user_info)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await complete_rift.finish()
                elif rift_type == "Boss战斗":
                    result, msg = await get_boss_battle_info(user_info, rift_rank, bot.self_id)
                    await send_forward_msg_list(bot, event, result)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await complete_rift.finish()
            elif rift_type == "宝物":
                msg = get_treasure_info(user_info, rift_rank)
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await complete_rift.finish()


# 终止探索秘境
@break_rift.handle(parameterless=[Cooldown(at_sender=True)])
async def break_rift_(bot: Bot, event: GroupMessageEvent):
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await break_rift.finish()
    user_id = user_info.user_id
    group_id = str(event.group_id)
    if group_id not in groups:
        msg = '本群尚未开启秘境，请联系管理员开启群秘境'
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await break_rift.finish()

    is_type, msg = check_user_type(user_id, 3)  # 需要在秘境的用户
    if not is_type:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await break_rift.finish()
    else:
        user_id = user_info.user_id
        rift_info = None
        try:
            rift_info = read_rift_data(user_id)
        except:
            msg = '发生未知错误！'
            sql_message.do_work(user_id, 0)
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await break_rift.finish()

        sql_message.do_work(user_id, 0)
        msg = f"已终止{rift_info['name']}秘境的探索！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await break_rift.finish()


@set_group_rift.handle(parameterless=[Cooldown(at_sender=True)])
async def set_group_rift_(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    mode = args.extract_plain_text().strip()
    group_id = str(event.group_id)
    is_in_group = is_in_groups(event)  # True在，False不在

    if mode == '开启':
        if is_in_group:
            msg = f'本群已开启群秘境，请勿重复开启!'
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await set_group_rift.finish()

        else:
            config['open'].append(group_id)
            savef(config)
            msg = f'已开启本群秘境!'
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await set_group_rift.finish()

    elif mode == '关闭':
        if is_in_group:
            config['open'].remove(group_id)
            savef(config)
            msg = f'已关闭本群秘境!'
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await set_group_rift.finish()
        else:
            msg = f'本群未开启群秘境!'
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await set_group_rift.finish()

    else:
        msg = __rift_help__
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await set_group_rift.finish()


def is_in_groups(event: GroupMessageEvent):
    return str(event.group_id) in groups
