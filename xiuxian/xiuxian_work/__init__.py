import os
from typing import Any, Tuple, Dict
from nonebot import on_regex, require, on_command
from nonebot.params import RegexGroup
from ..lay_out import assign_bot, Cooldown
from nonebot.adapters.onebot.v11 import (
    Bot,
    PRIVATE_FRIEND,
    GROUP,
    GroupMessageEvent,
    MessageSegment,
)
from ..xiuxian2_handle import XiuxianDateManage, OtherSet
from .work_handle import workhandle
from datetime import datetime
from ..xiuxian_opertion import do_is_work
from ..utils import check_user, check_user_type, get_msg_pic
from nonebot.log import logger
from .reward_data_source import PLAYERSDATA
from ..item_json import Items
from ..xiuxian_config import USERRANK, XiuConfig

# 定时任务
resetrefreshnum = require("nonebot_plugin_apscheduler").scheduler

work = {}  # 悬赏令信息记录
refreshnum: Dict[str, int] = {}  # 用户悬赏令刷新次数记录
sql_message = XiuxianDateManage()  # sql类
items = Items()
lscost = 500000  # 刷新灵石消耗
count = 3  # 免费次数


# 重置悬赏令刷新次数
@resetrefreshnum.scheduled_job("cron", hour=0, minute=0)
async def resetrefreshnum_():
    global refreshnum
    refreshnum = {}
    logger.info("用户悬赏令刷新次数重置成功")


last_work = on_command("最后的悬赏令", priority=15, block=True)
do_work = on_regex(
    r"^悬赏令(刷新|终止|结算|接取|帮助)?(\d+)?",
    priority=10,
    permission=PRIVATE_FRIEND | GROUP,
    block=True
)
__work_help__ = f"""
悬赏令帮助信息:
指令：
1、悬赏令:获取对应实力的悬赏令
2、悬赏令刷新:刷新当前悬赏令,每日免费{count}次
实力支持：江湖好手|搬血境|洞天境|化灵境|铭纹境|列阵境|尊者境|神火境|真一境|圣祭境|天神境|虚道境
3、悬赏令终止:终止当前悬赏令任务
4、悬赏令结算:结算悬赏奖励
5、悬赏令接取+编号：接取对应的悬赏令
6、最后的悬赏令:用于接了悬赏令却境界突破导致卡住的道友使用
""".strip()


@last_work.handle(parameterless=[Cooldown(cd_time=1.3,at_sender=True)])
async def last_work_(bot: Bot, event: GroupMessageEvent):
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await last_work.finish()
    user_id = user_info.user_id
    user_level = user_info.level
    is_type, msg = check_user_type(user_id, 2)  # 需要在悬赏令中的用户
    if (is_type and USERRANK[user_info.level] <= 22) or (
        is_type and user_info.exp >= sql_message.get_level_power("虚道境圆满")) or (
        is_type and int(user_info.exp) >= int(OtherSet().set_closing_type(user_level)) * XiuConfig().closing_exp_upper_limit    
        ):
        user_cd_message = sql_message.get_user_cd(user_id)
        work_time = datetime.strptime(
            user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
        )
        exp_time = (datetime.now() - work_time).seconds // 60  # 时长计算
        time2 = workhandle().do_work(
            # key=1, name=user_cd_message.scheduled_time  修改点
            key=1, name=user_cd_message.scheduled_time, level=user_level, exp=user_info.exp,
            user_id=user_info.user_id
        )
        if exp_time < time2:
            msg = f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await last_work.finish()
        else:
            msg, give_stone, s_o_f, item_id, big_suc = workhandle().do_work(
                2,
                work_list=user_cd_message.scheduled_time,
                level=user_level,
                exp=user_info.exp,
                user_id=user_info.user_id
            )
            item_flag = False
            item_msg = None
            item_info = None
            if item_id != 0:
                item_flag = True
                item_info = items.get_data_by_item_id(item_id)
                item_msg = f"{item_info['level']}:{item_info['name']}"
            if big_suc:  # 大成功
                sql_message.update_ls(user_id, give_stone * 2, 1)
                sql_message.do_work(user_id, 0)
                msg = f"悬赏令结算，{msg}获得报酬{give_stone * 2}枚灵石"
                # todo 战利品结算sql
                if item_flag:
                    sql_message.send_back(user_id, item_id, item_info['name'], item_info['type'], 1)
                    msg += f"，额外获得奖励：{item_msg}!"
                else:
                    msg += "!"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await last_work.finish()

            else:
                sql_message.update_ls(user_id, give_stone, 1)
                sql_message.do_work(user_id, 0)
                msg = f"悬赏令结算，{msg}获得报酬{give_stone}枚灵石"
                if s_o_f:  # 普通成功
                    if item_flag:
                        sql_message.send_back(user_id, item_id, item_info['name'], item_info['type'], 1)
                        msg += f"，额外获得奖励：{item_msg}!"
                    else:
                        msg += "!"
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await last_work.finish()

                else:  # 失败
                    msg += "!"
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await last_work.finish()
    else:
        msg = "不满足使用条件！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await last_work.finish()


@do_work.handle(parameterless=[Cooldown(cd_time=1.3, at_sender=True)])
async def do_work_(bot: Bot, event: GroupMessageEvent, args: Tuple[Any, ...] = RegexGroup()):
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    user_level = "虚道境圆满"
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await do_work.finish()
    user_id = user_info.user_id
    user_cd_message = sql_message.get_user_cd(user_id)
    if not os.path.exists(PLAYERSDATA / str(user_id) / "workinfo.json") and user_cd_message.type == 2:
        sql_message.do_work(user_id, 0)
        msg = f"悬赏令已更新，已重置道友的状态！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await do_work.finish()
    mode = args[0]  # 刷新、终止、结算、接取
    if USERRANK[user_info.level] <= 22:
        msg = f"道友的境界已过创业初期，悬赏令已经不能满足道友了！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await do_work.finish()
    if user_info.exp >= sql_message.get_level_power(user_level):
        msg = f"道友的实力已过创业初期，悬赏令已经不能满足道友了！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await do_work.finish()
    user_level = user_info.level
    if int(user_info.exp) >= int(OtherSet().set_closing_type(user_level)) * XiuConfig().closing_exp_upper_limit:
        # 获取下个境界需要的修为 * 1.5为闭关上限
        msg = f"道友的修为已经到达上限，悬赏令已无法在获得经验！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await do_work.finish()
    if user_cd_message.type == 1:
        msg = "已经在闭关中，请输入【出关】结束后才能获取悬赏令！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await do_work.finish()
    if user_cd_message.type == 3:
        msg = "道友在秘境中，请等待结束后才能获取悬赏令！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await do_work.finish()

    if mode is None:  # 接取逻辑
        if (user_cd_message.scheduled_time is None) or (user_cd_message.type == 0):
            try:
                msg = work[user_id].msg
            except KeyError:
                msg = "没有查到你的悬赏令信息呢，请刷新！"
        elif user_cd_message.type == 2:
            work_time = datetime.strptime(
                user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
            )
            exp_time = (datetime.now() - work_time).seconds // 60  # 时长计算
            time2 = workhandle().do_work(key=1, name=user_cd_message.scheduled_time, user_id=user_info.user_id)
            if exp_time < time2:
                msg = f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束"
            else:
                msg = f"进行中的悬赏令【{user_cd_message.scheduled_time}】，已结束，请输入【悬赏令结算】结算任务信息！"
        else:
            msg = "状态未知错误！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await do_work.finish()

    if mode == "刷新":  # 刷新逻辑
        stone_use = 0 #悬赏令刷新提示是否扣灵石
        if user_cd_message.type == 2:
            work_time = datetime.strptime(
                user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
            )
            exp_time = (datetime.now() - work_time).seconds // 60
            time2 = workhandle().do_work(key=1, name=user_cd_message.scheduled_time, user_id=user_info.user_id)
            if exp_time < time2:
                msg = f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束"
            else:
                msg = f"进行中的悬赏令【{user_cd_message.scheduled_time}】，已结束，请输入【悬赏令结算】结算任务信息！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await do_work.finish()

        try:
            usernums = refreshnum[user_id]
        except KeyError:
            usernums = 0

        freenum = count - usernums - 1
        if freenum < 0:
            freenum = 0
            if int(user_info.stone) < lscost:
                msg = f"道友的灵石不足以刷新，下次刷新消耗灵石：{lscost}枚"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await do_work.finish()
            else:
                sql_message.update_ls(user_id, lscost, 2)
                stone_use = 1

        work_msg = workhandle().do_work(0, level=user_level, exp=user_info.exp, user_id=user_id)
        n = 1
        work_list = []
        work_msg_f = f"☆------道友的个人悬赏令------☆\n"
        for i in work_msg:
            work_list.append([i[0], i[3]])
            work_msg_f += f"{n}、{get_work_msg(i)}"
            n += 1
        work_msg_f += f"(悬赏令每日免费刷新次数：{count}，超过{count}次后，下次刷新消耗灵石{lscost},今日可免费刷新次数：{freenum}次)"
        if int(stone_use) == 1:
            work_msg_f += f"\n道友消耗灵石{lscost}枚，成功刷新悬赏令"
        work[user_id] = do_is_work(user_id)
        work[user_id].msg = work_msg_f
        work[user_id].world = work_list

        refreshnum[user_id] = usernums + 1
        msg = work[user_id].msg
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await do_work.finish()

    elif mode == "终止":
        is_type, msg = check_user_type(user_id, 2)  # 需要在悬赏令中的用户
        if is_type:
            stone = 4000000
            sql_message.update_ls(user_id, stone, 2)
            sql_message.do_work(user_id, 0)
            msg = f"道友不讲诚信，被打了一顿灵石减少{stone},悬赏令已终止！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await do_work.finish()
        else:
            msg = "没有查到你的悬赏令信息呢，请刷新！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await do_work.finish()

    elif mode == "结算":
        is_type, msg = check_user_type(user_id, 2)  # 需要在悬赏令中的用户
        if is_type:
            user_cd_message = sql_message.get_user_cd(user_id)
            work_time = datetime.strptime(
                user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
            )
            exp_time = (datetime.now() - work_time).seconds // 60  # 时长计算
            time2 = workhandle().do_work(
                # key=1, name=user_cd_message.scheduled_time  修改点
                key=1, name=user_cd_message.scheduled_time, level=user_level, exp=user_info.exp,
                user_id=user_info.user_id
            )
            if exp_time < time2:
                msg = f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await do_work.finish()
            else:
                msg, give_exp, s_o_f, item_id, big_suc = workhandle().do_work(2,
                                                                              work_list=user_cd_message.scheduled_time,
                                                                              level=user_level,
                                                                              exp=user_info.exp,
                                                                              user_id=user_info.user_id)
                item_flag = False
                item_info = None
                item_msg = None
                if item_id != 0:
                    item_flag = True
                    item_info = items.get_data_by_item_id(item_id)
                    item_msg = f"{item_info['level']}:{item_info['name']}"
                if big_suc:  # 大成功
                    sql_message.update_exp(user_id, give_exp * 2)
                    sql_message.do_work(user_id, 0)
                    msg = f"悬赏令结算，{msg}增加修为{give_exp * 2}"
                    # todo 战利品结算sql
                    if item_flag:
                        sql_message.send_back(user_id, item_id, item_info['name'], item_info['type'], 1)
                        msg += f"，额外获得奖励：{item_msg}!"
                    else:
                        msg += "!"
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await do_work.finish()

                else:
                    sql_message.update_exp(user_id, give_exp)
                    sql_message.do_work(user_id, 0)
                    msg = f"悬赏令结算，{msg}增加修为{give_exp}"
                    if s_o_f:  # 普通成功
                        if item_flag:
                            sql_message.send_back(user_id, item_id, item_info['name'], item_info['type'], 1)
                            msg += f"，额外获得奖励：{item_msg}!"
                        else:
                            msg += "!"
                        if XiuConfig().img:
                            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                        else:
                            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                        await do_work.finish()

                    else:  # 失败
                        msg += "!"
                        if XiuConfig().img:
                            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                        else:
                            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                        await do_work.finish()
        else:
            msg = "没有查到你的悬赏令信息呢，请刷新！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await do_work.finish()

    elif mode == "接取":
        num = args[1]
        is_type, msg = check_user_type(user_id, 0)  # 需要无状态的用户
        if is_type:  # 接取逻辑
            if num is None or str(num) not in ['1', '2', '3']:
                msg = '请输入正确的任务序号'
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await do_work.finish()
            work_num = 1
            try:
                if work[user_id]:
                    work_num = int(num)  # 任务序号
                try:
                    get_work = work[user_id].world[work_num - 1]
                    sql_message.do_work(user_id, 2, get_work[0])
                    del work[user_id]
                    msg = f"接取任务【{get_work[0]}】成功"
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await do_work.finish()

                except IndexError:
                    msg = "没有这样的任务"
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await do_work.finish()

            except KeyError:
                msg = "没有查到你的悬赏令信息呢，请刷新！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await do_work.finish()
        else:
            msg = "没有查到你的悬赏令信息呢，请刷新！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await do_work.finish()

    elif mode == "帮助":
        msg = __work_help__
        if XiuConfig().img:
            pic = await get_msg_pic(msg, scale=False)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await do_work.finish()


def get_work_msg(work_):
    msg = f"{work_[0]},完成机率{work_[1]},基础报酬{work_[2]}修为,预计需{work_[3]}分钟{work_[4]}\n"
    return msg
