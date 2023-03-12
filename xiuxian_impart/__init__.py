import os
from pathlib import Path
import random
from nonebot import on_command, on_fullmatch
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    GROUP,
    Message,
    GroupMessageEvent,
    MessageSegment,
    ActionFailed
)
from ..lay_out import assign_bot, Cooldown
from ..utils import (
    check_user,
    get_msg_pic, send_forward_msg_list,
    CommandObjectID
)
from .impart_uitls import impart_check, get_rank, re_impart_data
from .impart_data import impart_data_json
from ..xiuxian_config import XiuConfig
from ..xn_xiuxian_impart import XIUXIAN_IMPART_BUFF
from .. import NICKNAME

xiuxian_impart = XIUXIAN_IMPART_BUFF()

cache_help = {}
img_path_ya = Path() / os.getcwd() / "data" / "xiuxian" / "卡图_压缩"
img_path = Path() / os.getcwd() / "data" / "xiuxian" / "卡图"
time_img = ["花园百花", "花园温室", "画屏春-倒影", "画屏春-繁月", "画屏春-花临",
            "画屏春-皇女", "画屏春-满桂", "画屏春-迷花", "画屏春-霎那", "画屏春-邀舞"]

impart_draw = on_fullmatch("传承抽卡", priority=16, permission=GROUP, block=True)
impart_back = on_command("传承背包", aliases={"我的传承背包"}, priority=15, permission=GROUP, block=True)
impart_data = on_command("传承信息", aliases={"我的传承信息", "我的传承"}, priority=10, permission=GROUP, block=True)
impart_help = on_command("传承帮助", aliases={"虚神界帮助"}, priority=8, permission=GROUP, block=True)
re_impart_load = on_fullmatch("加载传承数据", priority=45, permission=GROUP, block=True)
impart_img = on_command("传承卡图", aliases={"传承卡片"}, priority=50, permission=GROUP, block=True)

__impart_help__ = f"""
传承帮助信息:
指令:
1、传承抽卡:花费10颗思恋结晶获取一次传承卡片
2、传承信息:获取传承主要信息
3、传承背包:获取传承全部信息
4、加载传承数据:重新从卡片中加载所有传承属性(数据显示有误时可用)
5、传承卡图:加上卡片名字获取传承卡牌原画
思恋结晶获取方式:虚神界对决【俄罗斯轮盘修仙版】
双方共6次机会,6次中必有一次暴毙
获胜者将获取10颗思恋结晶并不消耗虚神界对决次数
失败者将获取5颗思恋结晶并且消耗一次虚神界对决次数
每天有三次虚神界对决次数
1、投影虚神界:将自己的分身投影到虚神界,将可被所有地域的道友挑战
2、虚神界列表:查找虚神界里所有的投影
3、虚神界对决:输入虚神界人物编号即可与对方对决,不输入编号将会与{NICKNAME}进行对决
4、虚神界修炼:加入对应的修炼时间,即可在虚神界修炼
"""


@impart_help.handle(parameterless=[Cooldown(at_sender=True)])
async def impart_help_(bot: Bot, event: GroupMessageEvent, session_id: int = CommandObjectID()):
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    if session_id in cache_help:
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(cache_help[session_id]))
        await impart_help.finish()
    else:
        msg = __impart_help__
        if XiuConfig().img:
            pic = await get_msg_pic(msg, scale=False)
            cache_help[session_id] = pic
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_help.finish()


@impart_img.handle(parameterless=[Cooldown(at_sender=True)])
async def impart_img_(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """传承卡图"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    img_name = args.extract_plain_text().strip()
    img = img_path / str(img_name + ".png")
    if not os.path.exists(img):
        msg = "没有找到此卡图！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_img.finish()
    else:
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(img))
        await impart_img.finish()


@impart_draw.handle(parameterless=[Cooldown(cd_time=3, at_sender=True)])
async def impart_draw_(bot: Bot, event: GroupMessageEvent):
    """传承抽卡"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_draw.finish()

    user_id = user_info.user_id
    impart_data_draw = await impart_check(user_id)
    if impart_data_draw is None:
        msg = "发生未知错误，多次尝试无果请找晓楠！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_draw.finish()
    if impart_data_draw.stone_num < 10:
        msg = "思恋结晶数量不足10个,无法抽卡!"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_draw.finish()
    else:
        if get_rank(user_id):
            img_list = impart_data_json.data_all_keys()
            reap_img = None
            try:
                reap_img = random.choice(img_list)
            except:
                msg = "请检查卡图数据完整！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await impart_draw.finish()
            list_tp = []
            if impart_data_json.data_person_add(user_id, reap_img):
                msg = ""
                msg += f"抽卡10次结果如下\n"
                msg += f"检测到传承背包已经存在卡片{reap_img}\n"
                msg += f"已转化为2880分钟闭关时间\n"
                msg += f"累计共获得3540分钟闭关时间!"

                list_tp.append(
                    {"type": "node", "data": {"name": f"道友{user_info.user_name}的传承抽卡", "uin": bot.self_id,
                                              "content": msg}})
                img = MessageSegment.image(img_path_ya / str(reap_img + ".png"))
                list_tp.append(
                    {"type": "node", "data": {"name": f"道友{user_info.user_name}的传承抽卡", "uin": bot.self_id,
                                              "content": img}})
                random.shuffle(time_img)
                for x in time_img[:9]:
                    img = MessageSegment.image(img_path_ya / str(x + ".png"))
                    list_tp.append(
                        {"type": "node", "data": {"name": f"道友{user_info.user_name}的传承抽卡", "uin": bot.self_id,
                                                  "content": img}})
                try:
                    await send_forward_msg_list(bot, event, list_tp)
                except ActionFailed:
                    msg = "未知原因，抽卡失败!"
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await impart_draw.finish()
                xiuxian_impart.add_impart_exp_day(3540, user_id)
                xiuxian_impart.update_stone_num(10, user_id, 2)
                xiuxian_impart.update_impart_wish(0, user_id)
                # 更新传承数据
                await re_impart_data(user_id)
                await impart_draw.finish()
            else:
                msg = ""
                msg += f"抽卡10次结果如下,获得新的传承卡片{reap_img}\n"
                msg += f"累计共获得660分钟闭关时间!"
                list_tp.append(
                    {"type": "node", "data": {"name": f"道友{user_info.user_name}的传承抽卡", "uin": bot.self_id,
                                              "content": msg}})
                img = MessageSegment.image(img_path_ya / str(reap_img + ".png"))
                list_tp.append(
                    {"type": "node", "data": {"name": f"道友{user_info.user_name}的传承抽卡", "uin": bot.self_id,
                                              "content": img}})
                random.shuffle(time_img)
                for x in time_img[:9]:
                    img = MessageSegment.image(img_path_ya / str(x + ".png"))
                    list_tp.append(
                        {"type": "node", "data": {"name": f"道友{user_info.user_name}的传承抽卡", "uin": bot.self_id,
                                                  "content": img}})
                try:
                    await send_forward_msg_list(bot, event, list_tp)
                except ActionFailed:
                    msg = "消息发送失败，抽卡失败!"
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await impart_draw.finish()
                xiuxian_impart.add_impart_exp_day(660, user_id)
                xiuxian_impart.update_stone_num(10, user_id, 2)
                xiuxian_impart.update_impart_wish(0, user_id)
                # 更新传承数据
                await re_impart_data(user_id)
                await impart_draw.finish()
        else:
            list_tp = []
            msg = ""
            msg += f"抽卡10次结果如下!\n"
            msg += f"累计共获得660分钟闭关时间!"
            list_tp.append(
                {"type": "node", "data": {"name": f"道友{user_info.user_name}的传承抽卡", "uin": bot.self_id,
                                          "content": msg}})
            random.shuffle(time_img)
            for x in time_img:
                img = MessageSegment.image(img_path_ya / str(x + ".png"))
                list_tp.append(
                    {"type": "node", "data": {"name": f"道友{user_info.user_name}的传承抽卡", "uin": bot.self_id,
                                              "content": img}})
            try:
                await send_forward_msg_list(bot, event, list_tp)
            except ActionFailed:
                msg = "未知原因，抽卡失败!"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await impart_draw.finish()
            xiuxian_impart.add_impart_exp_day(660, user_id)
            xiuxian_impart.update_stone_num(10, user_id, 2)
            xiuxian_impart.add_impart_wish(10, user_id)
            await impart_draw.finish()


@impart_back.handle(parameterless=[Cooldown(at_sender=True)])
async def impart_back_(bot: Bot, event: GroupMessageEvent):
    """传承背包"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_back.finish()
    user_id = user_info.user_id
    impart_data_draw = await impart_check(user_id)
    if impart_data_draw is None:
        msg = "发生未知错误，多次尝试无果请找晓楠！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_back.finish()
    img_tp = impart_data_json.data_person_list(user_id)
    list_tp = []
    img = None
    for x in range(len(img_tp)):
        img += MessageSegment.image(img_path_ya / str(img_tp[x] + ".png"))
    txt_back = f"""--道友{user_info.user_name}的传承物资--
思恋结晶：{impart_data_draw.stone_num}颗
抽卡次数：{impart_data_draw.wish}/90次
累计闭关时间：{impart_data_draw.exp_day}分钟
"""
    txt_tp = f"""--道友{user_info.user_name}的传承总属性--
攻击提升:{int(impart_data_draw.impart_atk_per * 100)}%
气血提升:{int(impart_data_draw.impart_hp_per * 100)}%
真元提升:{int(impart_data_draw.impart_mp_per * 100)}%
会心提升：{int(impart_data_draw.impart_know_per * 100)}%
会心伤害提升：{int(impart_data_draw.impart_burst_per * 100)}%
闭关经验提升：{int(impart_data_draw.impart_exp_up * 100)}%
炼丹收获数量提升：{impart_data_draw.impart_mix_per}颗
灵田收取数量提升：{impart_data_draw.impart_reap_per}颗
每日双修次数提升：{impart_data_draw.impart_two_exp}次
boss战攻击提升:{int(impart_data_draw.boss_atk * 100)}%
"""
    list_tp.append(
        {"type": "node", "data": {"name": f"道友{user_info.user_name}的传承背包", "uin": bot.self_id,
                                  "content": txt_back}})
    list_tp.append(
        {"type": "node", "data": {"name": f"道友{user_info.user_name}的传承背包", "uin": bot.self_id,
                                  "content": txt_tp}})
    list_tp.append(
        {"type": "node", "data": {"name": f"道友{user_info.user_name}的传承背包", "uin": bot.self_id,
                                  "content": img}})
    try:
        await send_forward_msg_list(bot, event, list_tp)
    except ActionFailed:
        msg = "获取传承背包数据失败！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_back.finish()
    await impart_back.finish()


@re_impart_load.handle(parameterless=[Cooldown(at_sender=True)])
async def re_impart_load_(bot: Bot, event: GroupMessageEvent):
    """加载传承数据"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await re_impart_load.finish()
    user_id = user_info.user_id
    impart_data_draw = await impart_check(user_id)
    if impart_data_draw is None:
        msg = "发生未知错误，多次尝试无果请找晓楠！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await re_impart_load.finish()
    # 更新传承数据
    info = await re_impart_data(user_id)
    if info:
        msg = "传承数据加载完成！"
    else:
        msg = "传承数据加载失败！"
    if XiuConfig().img:
        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
    else:
        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
    await re_impart_load.finish()


@impart_data.handle(parameterless=[Cooldown(at_sender=True)])
async def re_impart_load_(bot: Bot, event: GroupMessageEvent):
    """传承信息"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_data.finish()
    user_id = user_info.user_id
    impart_data_draw = await impart_check(user_id)
    if impart_data_draw is None:
        msg = "发生未知错误，多次尝试无果请找晓楠！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_data.finish()

    msg = f"""--道友{user_info.user_name}的传承物资--
思恋结晶：{impart_data_draw.stone_num}颗
抽卡次数：{impart_data_draw.wish}/90次
累计闭关时间：{impart_data_draw.exp_day}分钟
    """
    if XiuConfig().img:
        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
    else:
        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
    await impart_data.finish()



