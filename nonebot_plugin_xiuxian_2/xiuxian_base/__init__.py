#!usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import re
from datetime import datetime
from ..lay_out import assign_bot, Cooldown
from nonebot import require
from nonebot.adapters.onebot.v11 import (
    Bot,
    GROUP,
    Message,
    GroupMessageEvent,
    MessageSegment,
    ActionFailed
)
from ..read_buff import UserBuffDate
from nonebot import on_command, on_fullmatch
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from nonebot.params import CommandArg
from ..data_source import jsondata
from ..xiuxian2_handle import XiuxianDateManage, XiuxianJsonDate, OtherSet
from ..xiuxian_config import XiuConfig, JsonConfig
from ..utils import (
    check_user, send_forward_msg,
    get_msg_pic, number_to,
    CommandObjectID
)
from ..item_json import Items
from ..xn_xiuxian_impart import XIUXIAN_IMPART_BUFF, leave_harm_time

# 定时任务
scheduler = require("nonebot_plugin_apscheduler").scheduler
cache_help = {}
cache_help_fk = {}
sql_message = XiuxianDateManage()  # sql类
xiuxian_impart = XIUXIAN_IMPART_BUFF()

run_xiuxian = on_fullmatch("我要修仙", priority=8, permission=GROUP, block=True)
restart = on_fullmatch("重入仙途", permission=GROUP, priority=7, block=True)
sign_in = on_fullmatch("修仙签到", priority=13, permission=GROUP, block=True)
help_in = on_fullmatch("修仙帮助", priority=12, permission=GROUP, block=True)
warring_help = on_fullmatch("风控帮助", priority=12, permission=GROUP, block=True)
rank = on_command("排行榜", aliases={"修仙排行榜", "灵石排行榜", "战力排行榜", "境界排行榜", "宗门排行榜"},
                priority=7, permission=GROUP, block=True)
remaname = on_command("改名", priority=5, permission=GROUP, block=True)
level_up = on_fullmatch("突破", priority=6, permission=GROUP, block=True)
level_up_dr = on_fullmatch("渡厄突破", priority=7, permission=GROUP, block=True)
level_up_zj = on_fullmatch("直接突破", priority=7, permission=GROUP, block=True)
give_stone = on_command("送灵石", priority=5, permission=GROUP, block=True)
steal_stone = on_command("偷灵石", aliases={"飞龙探云手"}, priority=4, permission=GROUP, block=True)
gm_command = on_command("神秘力量", permission=SUPERUSER, priority=10, block=True)
rob_stone = on_command("抢劫", aliases={"抢灵石"}, priority=5, permission=GROUP, block=True)
restate = on_command("重置状态", permission=SUPERUSER, priority=12, block=True)
open_xiuxian = on_command("启用修仙功能", aliases={'禁用修仙功能'}, permission=SUPERUSER, priority=5, block=True)
user_leveluprate = on_command('我的突破概率', aliases={'突破概率'}, priority=5, permission=GROUP, block=True)
xiuxian_updata_level = on_fullmatch('修仙适配', priority=15, permission=GROUP, block=True)
xiuxian_uodata_data = on_fullmatch('更新记录', priority=15, permission=GROUP, block=True)

__xiuxian_notes__ = f"""
指令：
1、我要修仙:进入修仙模式
2、我的修仙信息:获取修仙数据
3、修仙签到:获取灵石及修为
4、重入仙途:重置灵根数据,每次{XiuConfig().remake}灵石
5、风控帮助:发送"风控帮助"获取
6、改名xx:修改你的道号
7、突破:修为足够后,可突破境界（一定几率失败）
8、闭关、出关、灵石出关、灵石修炼、双修:修炼增加修为,挂机功能
9、送灵石100@xxx,偷灵石@xxx,抢灵石@xxx
10、排行榜:修仙排行榜,灵石排行榜,战力排行榜,宗门排行榜
11、悬赏令帮助:获取悬赏令帮助信息
12、我的状态:查看当前HP,我的功法：查看当前技能
13、宗门系统:发送"宗门帮助"获取
14、灵庄系统:发送"灵庄帮助"获取
15、世界BOSS:发送"世界boss帮助"获取
16、功法/灵田：发送“功法帮助/灵田帮助”查看，当前获取途径看“宗门帮助”
17、背包/交友：发送"背包帮助"获取
18、秘境系统:发送"秘境帮助"获取
19、炼丹帮助:炼丹功能
20、传承系统:发送"传承帮助/虚神界帮助"获取
21、修仙适配:将1的境界适配到2
22、启用/禁用修仙功能：当前群开启或关闭修仙功能
23、更新记录:获取插件最新内容
""".strip()

__warring_help__ = f"""
配置地址:修仙插件下xiuxian_config.py
self.put_bot = []  # 接收消息qq,主qq,框架将只处理此qq的消息.
self.main_bo = []  # 负责发送消息的qq
self.shield_group = []  # 屏蔽的群聊
self.layout_bot_dict = {{}}  # QQ所负责的群聊{{群 :bot}}   其中 bot类型 []或str 
""".strip()

__xiuxian_updata_data__ = f"""
## 更新2023.3.1 - 2023.3.6
1.修复已知bug
2.支持每个群boss刷新时间定制
3.支持适配修仙1的境界
3.宗门可以根据qq号踢人,宗门成员查看获得qq号
4.支持随机存档背景
5.支持批量使用丹药
6.支持批量炼金和炼金绑定丹药
7.修改了世界积分价格,需要删除boss模块下的config.json生效
8.增加了修仙全局命令调用锁,默认一分钟五次
9.增加隐藏职业：器师
器师：指依托于大宗门下的炼器士，其修为一般很低，但不可小觑，因为一般是大修士的转生与亲信，替大修士完成红尘历练。
更新类容：## 更新2023.3.11
1.修改背包容量
2.坊市支持批量上架和购买
3.解决手机部分图片需要点开才能看到字的问题
""".strip()

# 重置每日签到
@scheduler.scheduled_job("cron", hour=0, minute=0)
async def xiuxian_sing_():
    sql_message.singh_remake()
    logger.info("每日修仙签到重置成功！")


@xiuxian_uodata_data.handle(parameterless=[Cooldown(at_sender=True)])
async def mix_elixir_help_(bot: Bot, event: GroupMessageEvent):
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    msg = __xiuxian_updata_data__
    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
    await xiuxian_uodata_data.finish()


@run_xiuxian.handle(parameterless=[Cooldown(at_sender=True)])
async def run_xiuxian_(bot: Bot, event: GroupMessageEvent):
    """加入修仙"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    user_id = event.get_user_id()
    user_name = (
        event.sender.card if event.sender.card else event.sender.nickname
    )  # 获取为用户名
    root, root_type = XiuxianJsonDate().linggen_get()  # 获取灵根，灵根类型
    rate = sql_message.get_root_rate(root_type)  # 灵根倍率
    power = 100 * float(rate)  # 战力=境界的power字段 * 灵根的rate字段
    create_time = str(datetime.now())
    msg = sql_message.create_user(
        user_id, root, root_type, int(power), create_time, user_name
    )
    try:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await run_xiuxian.finish()
    except ActionFailed:
        await run_xiuxian.finish("修仙界网络堵塞，发送失败!", reply_message=True)


@sign_in.handle(parameterless=[Cooldown(at_sender=True)])
async def sign_in_(bot: Bot, event: GroupMessageEvent):
    """修仙签到"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await sign_in.finish()
    user_id = user_info.user_id
    result = sql_message.get_sign(user_id)
    msg = result
    try:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await sign_in.finish()
    except ActionFailed:
        await sign_in.finish("修仙界网络堵塞，发送失败!", reply_message=True)


@help_in.handle(parameterless=[Cooldown(at_sender=True)])
async def help_in_(bot: Bot, event: GroupMessageEvent, session_id: int = CommandObjectID()):
    """修仙帮助"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    if session_id in cache_help:
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(cache_help[session_id]))
        await help_in.finish()
    else:
        msg = __xiuxian_notes__
        if XiuConfig().img:
            pic = await get_msg_pic(msg, scale=False)
            cache_help[session_id] = pic
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await help_in.finish()


@warring_help.handle(parameterless=[Cooldown(at_sender=True)])
async def warring_help_(bot: Bot, event: GroupMessageEvent, session_id: int = CommandObjectID()):
    """风控帮助"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    if session_id in cache_help_fk:
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(cache_help_fk[session_id]))
        await warring_help.finish()
    else:
        msg = __warring_help__
        if XiuConfig().img:
            pic = await get_msg_pic(msg, scale=False)
            cache_help_fk[session_id] = pic
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await warring_help.finish()


@restart.handle(parameterless=[Cooldown(90, at_sender=True)])
async def restart_(bot: Bot, event: GroupMessageEvent):
    """刷新灵根信息"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await restart.finish()
    user_id = user_info.user_id
    name, root_type = XiuxianJsonDate().linggen_get()
    msg = sql_message.ramaker(name, root_type, user_id)
    sql_message.update_power2(user_id)  # 更新战力
    try:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await restart.finish()    
    except ActionFailed:
        await restart.finish("修仙界网络堵塞，发送失败!", reply_message=True)


@rank.handle(parameterless=[Cooldown(at_sender=True)])
async def rank_(bot: Bot, event: GroupMessageEvent):
    """排行榜"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    message = str(event.message)
    rank_msg = r'[\u4e00-\u9fa5]+'
    message = re.findall(rank_msg, message)
    if message:
        message = message[0]
    if message == "排行榜" or message == "修仙排行榜" or message == "境界排行榜":
        p_rank = sql_message.realm_top()
        msg = f"✨位面境界排行榜TOP10✨\n"
        num = 0
        for i in p_rank:
            num += 1
            msg += f"第{num}位 {i[0]} {i[1]},修为{number_to(i[2])}\n"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await rank.finish()
    elif message == "灵石排行榜":
        a_rank = sql_message.stone_top()
        msg = f"✨位面灵石排行榜TOP10✨\n"
        num = 0
        for i in a_rank:
            num += 1
            msg += f"第{num}位  {i[0]}  灵石：{number_to(i[1])}枚\n"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await rank.finish()
    elif message == "战力排行榜":
        c_rank = sql_message.power_top()
        msg = f"✨位面战力排行榜TOP10✨\n"
        num = 0
        for i in c_rank:
            num += 1
            msg += f"第{num}位  {i[0]}  战力：{number_to(i[1])}\n"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await rank.finish()
    elif message in ["宗门排行榜", "宗门建设度排行榜"]:
        s_rank = sql_message.scale_top()
        msg = f"✨位面宗门建设排行榜TOP10✨\n"
        num = 0
        for i in s_rank:
            num += 1
            msg += f"第{num}位  {i[1]}  建设度：{number_to(i[2])}\n"
            if num == 10:
                break
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await rank.finish()


@remaname.handle(parameterless=[Cooldown(at_sender=True)])
async def remaname_(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """修改道号"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await remaname.finish()
    user_id = user_info.user_id
    user_name = args.extract_plain_text().strip()
    len_username = len(user_name.encode('gbk'))
    if len_username > 20:
        msg = "道号长度过长，请修改后重试！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await remaname.finish()
    mes = sql_message.update_user_name(user_id, user_name)
    msg = mes
    if XiuConfig().img:
        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
    else:
        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
    await remaname.finish()


@level_up.handle(parameterless=[Cooldown(at_sender=True)])
async def level_up_(bot: Bot, event: GroupMessageEvent):
    """突破"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await level_up.finish()
    user_id = user_info.user_id
    if user_info.hp is None:
        # 判断用户气血是否为空
        sql_message.update_user_hp(user_id)
    user_msg = sql_message.get_user_message(user_id)  # 用户信息
    user_leveluprate = int(user_msg.level_up_rate)  # 用户失败次数加成
    level_cd = user_msg.level_up_cd
    if level_cd:
        # 校验是否存在CD
        time_now = datetime.now()
        cd = OtherSet().date_diff(time_now, level_cd)  # 获取second
        if cd < XiuConfig().level_up_cd * 60:
            # 如果cd小于配置的cd，返回等待时间
            msg = "目前无法突破，还需要{}分钟".format(XiuConfig().level_up_cd - (cd // 60))
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await level_up.finish()
    else:
        pass

    level_name = user_msg.level  # 用户境界
    level_rate = jsondata.level_rate_data()[level_name]  # 对应境界突破的概率
    user_backs = sql_message.get_back_msg(user_id)  # list(back)
    items = Items()
    pause_flag = False
    elixir_name = None
    elixir_desc = None
    if user_backs is not None:
        for back in user_backs:
            if int(back.goods_id) == 1999:  # 检测到有对应丹药
                pause_flag = True
                elixir_name = back.goods_name
                elixir_desc = items.get_data_by_item_id(1999)['desc']
                break
    if pause_flag:
        msg = f"由于检测到背包有丹药：{elixir_name}，效果：{elixir_desc}，突破已经准备就绪，请发送 ，【渡厄突破】 或 【直接突破】来选择是否使用丹药突破！本次突破概率为：{level_rate + user_leveluprate}% "
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await level_up.finish()
    else:
        msg = f"由于检测到背包没有【渡厄丹】，突破已经准备就绪，请发送，【直接突破】来突破！请注意，本次突破失败将会损失部分修为，本次突破概率为：{level_rate + user_leveluprate}% "
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await level_up.finish()


@level_up_zj.handle(parameterless=[Cooldown(at_sender=True)])
async def level_up_zj_(bot: Bot, event: GroupMessageEvent):
    """直接 突破"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await level_up_zj.finish()
    user_id = user_info.user_id
    if user_info.hp is None:
        # 判断用户气血是否为空
        sql_message.update_user_hp(user_id)
    user_msg = sql_message.get_user_message(user_id)  # 用户信息
    level_cd = user_msg.level_up_cd
    if level_cd:
        # 校验是否存在CD
        time_now = datetime.now()
        cd = OtherSet().date_diff(time_now, level_cd)  # 获取second
        if cd < XiuConfig().level_up_cd * 60:
            # 如果cd小于配置的cd，返回等待时间
            msg = "目前无法突破，还需要{}分钟".format(XiuConfig().level_up_cd - (cd // 60))
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await level_up_zj.finish()
    else:
        pass
    level_name = user_msg.level  # 用户境界
    exp = user_msg.exp  # 用户修为
    level_rate = jsondata.level_rate_data()[level_name]  # 对应境界突破的概率
    user_leveluprate = int(user_msg.level_up_rate)  # 用户失败次数加成
    le = OtherSet().get_type(exp, level_rate + user_leveluprate, level_name)
    if le == "失败":
        # 突破失败
        sql_message.updata_level_cd(user_id)  # 更新突破CD
        # 失败惩罚，随机扣减修为
        percentage = random.randint(
            XiuConfig().level_punishment_floor, XiuConfig().level_punishment_limit
        )
        now_exp = int(int(exp) * (percentage / 100))
        sql_message.update_j_exp(user_id, now_exp)  # 更新用户修为
        nowhp = user_msg.hp - (now_exp / 2) if (user_msg.hp - (now_exp / 2)) > 0 else 1
        nowmp = user_msg.mp - now_exp if (user_msg.mp - now_exp) > 0 else 1
        sql_message.update_user_hp_mp(user_id, nowhp, nowmp)  # 修为掉了，血量、真元也要掉
        update_rate = 1 if int(level_rate * XiuConfig().level_up_probability) <= 1 else int(
            level_rate * XiuConfig().level_up_probability)  # 失败增加突破几率
        sql_message.update_levelrate(user_id, user_leveluprate + update_rate)
        msg = "道友突破失败,境界受损,修为减少{}，下次突破成功率增加{}%，道友不要放弃！".format(now_exp, update_rate)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await level_up_zj.finish()

    elif type(le) == list:
        # 突破成功
        sql_message.updata_level(user_id, le[0])  # 更新境界
        sql_message.update_power2(user_id)  # 更新战力
        sql_message.updata_level_cd(user_id)  # 更新CD
        sql_message.update_levelrate(user_id, 0)
        sql_message.update_user_hp(user_id)  # 重置用户HP，mp，atk状态
        msg = "恭喜道友突破{}成功".format(le[0])
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await level_up_zj.finish()
    else:
        # 最高境界
        msg = le
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await level_up_zj.finish()


@level_up_dr.handle(parameterless=[Cooldown(at_sender=True)])
async def level_up_dr_(bot: Bot, event: GroupMessageEvent):
    """渡厄 突破"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await level_up_dr.finish()
    user_id = user_info.user_id
    if user_info.hp is None:
        # 判断用户气血是否为空
        sql_message.update_user_hp(user_id)
    user_msg = sql_message.get_user_message(user_id)  # 用户信息
    level_cd = user_msg.level_up_cd
    if level_cd:
        # 校验是否存在CD
        time_now = datetime.now()
        cd = OtherSet().date_diff(time_now, level_cd)  # 获取second
        if cd < XiuConfig().level_up_cd * 60:
            # 如果cd小于配置的cd，返回等待时间
            msg = "目前无法突破，还需要{}分钟".format(XiuConfig().level_up_cd - (cd // 60))
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await level_up_dr.finish()
    else:
        pass
    elixir_name = "渡厄丹"
    level_name = user_msg.level  # 用户境界
    exp = user_msg.exp  # 用户修为
    level_rate = jsondata.level_rate_data()[level_name]  # 对应境界突破的概率
    user_leveluprate = int(user_msg.level_up_rate)  # 用户失败次数加成
    le = OtherSet().get_type(exp, level_rate + user_leveluprate, level_name)
    user_backs = sql_message.get_back_msg(user_id)  # list(back)
    pause_flag = False
    if user_backs is not None:
        for back in user_backs:
            if int(back.goods_id) == 1999:  # 检测到有对应丹药
                pause_flag = True
                elixir_name = back.goods_name
                break

    if le == "失败":
        # 突破失败
        sql_message.updata_level_cd(user_id)  # 更新突破CD
        if pause_flag:
            # todu，丹药减少的sql
            sql_message.update_back_j(user_id, 1999, use_key=1)
            update_rate = 1 if int(level_rate * XiuConfig().level_up_probability) <= 1 else int(
                level_rate * XiuConfig().level_up_probability)  # 失败增加突破几率
            sql_message.update_levelrate(user_id, user_leveluprate + update_rate)
            msg = f"道友突破失败，但是使用了丹药{elixir_name}，本次突破失败不扣除修为下次突破成功率增加{update_rate}%，道友不要放弃！"
        else:
            # 失败惩罚，随机扣减修为
            percentage = random.randint(
                XiuConfig().level_punishment_floor, XiuConfig().level_punishment_limit
            )
            now_exp = int(int(exp) * (percentage / 100))
            sql_message.update_j_exp(user_id, now_exp)  # 更新用户修为
            nowhp = user_msg.hp - (now_exp / 2) if (user_msg.hp - (now_exp / 2)) > 0 else 1
            nowmp = user_msg.mp - now_exp if (user_msg.mp - now_exp) > 0 else 1
            sql_message.update_user_hp_mp(user_id, nowhp, nowmp)  # 修为掉了，血量、真元也要掉
            update_rate = 1 if int(level_rate * XiuConfig().level_up_probability) <= 1 else int(
                level_rate * XiuConfig().level_up_probability)  # 失败增加突破几率
            sql_message.update_levelrate(user_id, user_leveluprate + update_rate)
            msg = "没有检测到{}，道友突破失败,境界受损,修为减少{}，下次突破成功率增加{}%，道友不要放弃！".format(elixir_name, now_exp, update_rate)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await level_up_dr.finish()

    elif type(le) == list:
        # 突破成功
        sql_message.updata_level(user_id, le[0])  # 更新境界
        sql_message.update_power2(user_id)  # 更新战力
        sql_message.updata_level_cd(user_id)  # 更新CD
        sql_message.update_levelrate(user_id, 0)
        sql_message.update_user_hp(user_id)  # 重置用户HP，mp，atk状态
        msg = "恭喜道友突破{}成功".format(le[0])
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await level_up_dr.finish()
    else:
        # 最高境界
        msg = le
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await level_up_dr.finish()


@user_leveluprate.handle(parameterless=[Cooldown(at_sender=True)])
async def user_leveluprate_(bot: Bot, event: GroupMessageEvent):
    """我的突破概率"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await user_leveluprate.finish()
    user_id = user_info.user_id
    user_msg = sql_message.get_user_message(user_id)  # 用户信息
    leveluprate = int(user_msg.level_up_rate)  # 用户失败次数加成
    level_name = user_msg.level  # 用户境界
    level_rate = jsondata.level_rate_data()[level_name]  # 对应境界突破的概率
    msg = f"道友下一次突破成功概率为{level_rate + leveluprate}%"
    if XiuConfig().img:
        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
    else:
        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
    await user_leveluprate.finish()


@give_stone.handle(parameterless=[Cooldown(at_sender=True)])
async def give_stone_(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """送灵石"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await give_stone.finish()
    user_id = user_info.user_id
    user_stone_num = user_info.stone
    give_qq = None  # 艾特的时候存到这里
    msg = args.extract_plain_text().strip()
    stone_num = re.findall("\d+", msg)  # 灵石数
    nick_name = re.findall("\D+", msg)  # 道号
    if stone_num:
        pass
    else:
        msg = "请输入正确的灵石数量！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await give_stone.finish()
    give_stone_num = stone_num[0]
    if int(give_stone_num) > int(user_stone_num):
        msg = "道友的灵石不够，请重新输入！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await give_stone.finish()
    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")
    if give_qq:
        if str(give_qq) == str(user_id):
            msg = "请不要送灵石给自己！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await give_stone.finish()
        else:
            give_user = sql_message.get_user_message(give_qq)
            if give_user:
                sql_message.update_ls(user_id, give_stone_num, 2)  # 减少用户灵石
                give_stone_num2 = int(give_stone_num) * 0.1
                num = int(give_stone_num) - int(give_stone_num2)
                sql_message.update_ls(give_qq, num, 1)  # 增加用户灵石
                msg = "共赠送{}枚灵石给{}道友！收取手续费{}枚".format(
                    give_stone_num, give_user.user_name, int(give_stone_num2)
                )
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await give_stone.finish()
            else:
                msg = "对方未踏入修仙界，不可赠送！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await give_stone.finish()

    if nick_name:
        give_message = sql_message.get_user_message2(nick_name[0])
        if give_message:
            if give_message.user_name == user_info.user_name:
                msg = "请不要送灵石给自己！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await give_stone.finish()
            else:
                sql_message.update_ls(user_id, give_stone_num, 2)  # 减少用户灵石
                give_stone_num2 = int(give_stone_num) * 0.1
                num = int(give_stone_num) - int(give_stone_num2)
                sql_message.update_ls(give_message.user_id, num, 1)  # 增加用户灵石
                msg = "共赠送{}枚灵石给{}道友！收取手续费{}枚".format(
                    give_stone_num, give_message.user_name, int(give_stone_num2)
                )
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await give_stone.finish()
        else:
            msg = "对方未踏入修仙界，不可赠送！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await give_stone.finish()

    else:
        msg = "未获到对方信息，请输入正确的道号！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await give_stone.finish()


# 偷灵石
@steal_stone.handle(parameterless=[Cooldown(XiuConfig().tou_cd, at_sender=True)])
async def steal_stone_(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await steal_stone.finish()
    user_id = user_info.user_id
    steal_user = None
    steal_user_stone = None
    user_stone_num = user_info.stone
    steal_qq = None  # 艾特的时候存到这里, 要偷的人
    coststone_num = XiuConfig().tou
    if int(coststone_num) > int(user_stone_num):
        msg = '道友的偷窃准备(灵石)不足，请打工之后再切格瓦拉！'
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await steal_stone.finish()
    for arg in args:
        if arg.type == "at":
            steal_qq = arg.data.get('qq', '')
    if steal_qq:
        if steal_qq == user_id:
            msg = "请不要偷自己刷成就！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await steal_stone.finish()
        else:
            steal_user = sql_message.get_user_message(steal_qq)
            steal_user_stone = steal_user.stone
    if steal_user:
        steal_success = random.randint(0, 100)
        result = OtherSet().get_power_rate(user_info.power, steal_user.power)
        if isinstance(result, int):
            if int(steal_success) > result:
                sql_message.update_ls(user_id, coststone_num, 2)  # 减少手续费
                sql_message.update_ls(steal_qq, coststone_num, 1)  # 增加被偷的人的灵石
                msg = '道友偷窃失手了，被对方发现并被派去华哥厕所义务劳工！赔款{}灵石'.format(coststone_num)
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await steal_stone.finish()
            get_stone = random.randint(int(XiuConfig().tou_lower_limit * steal_user_stone),
                                       int(XiuConfig().tou_upper_limit * steal_user_stone))
            if int(get_stone) > int(steal_user_stone):
                sql_message.update_ls(user_id, steal_user_stone, 1)  # 增加偷到的灵石
                sql_message.update_ls(steal_qq, steal_user_stone, 2)  # 减少被偷的人的灵石
                msg = "{}道友已经被榨干了~".format(steal_user.user_name)
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await steal_stone.finish()
            else:
                sql_message.update_ls(user_id, get_stone, 1)  # 增加偷到的灵石
                sql_message.update_ls(steal_qq, get_stone, 2)  # 减少被偷的人的灵石
                msg = "共偷取{}道友{}枚灵石！".format(steal_user.user_name, get_stone)
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await steal_stone.finish()
        else:
            msg = result
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await steal_stone.finish()
    else:
        msg = "对方未踏入修仙界，不要对杂修出手！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await steal_stone.finish()


# GM加灵石
@gm_command.handle(parameterless=[Cooldown(at_sender=True)])
async def gm_command_(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    give_qq = None  # 艾特的时候存到这里
    msg = args.extract_plain_text().strip()
    stone_num = re.findall("\d+", msg)  ## 灵石数
    nick_name = re.findall("\D+", msg)  ## 道号
    give_stone_num = stone_num[0]
    if 1 <= int(give_stone_num) <= 100000000:
        pass
    else:
        msg = "请输入正确的灵石数量！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await gm_command.finish()
    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")
    if give_qq:
        give_user = sql_message.get_user_message(give_qq)
        if give_user:
            sql_message.update_ls(give_qq, give_stone_num, 1)  # 增加用户灵石
            msg = "共赠送{}枚灵石给{}道友！".format(give_stone_num, give_user.user_name)
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await gm_command.finish()
        else:
            msg = "对方未踏入修仙界，不可赠送！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await gm_command.finish()
    elif nick_name:
        give_message = sql_message.get_user_message2(nick_name[0])
        if give_message:
            sql_message.update_ls(give_message.user_id, give_stone_num, 1)  # 增加用户灵石
            msg = "共赠送{}枚灵石给{}道友！".format(give_stone_num, give_message.user_name)
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await gm_command.finish()
        else:
            msg = "对方未踏入修仙界，不可赠送！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await gm_command.finish()
    else:
        sql_message.update_ls_all(give_stone_num)
        msg = f"全服通告：赠送所有用户{give_stone_num}灵石,请注意查收！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await gm_command.finish()


@rob_stone.handle(parameterless=[Cooldown(cd_time=600 ,at_sender=True)])
async def rob_stone_(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """抢灵石
            player1 = {
            "NAME": player,
            "HP": player,
            "ATK": ATK,
            "COMBO": COMBO
        }"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await give_stone.finish()
    if user_info.root == "器师":
        msg = "目前职业无法抢劫！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await rob_stone.finish()
    user_id = user_info.user_id
    give_qq = None  # 艾特的时候存到这里
    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")
    player1 = {"user_id": None, "道号": None, "气血": None, "攻击": None, "真元": None, '会心': None, '爆伤': None, '防御': 0}
    player2 = {"user_id": None, "道号": None, "气血": None, "攻击": None, "真元": None, '会心': None, '爆伤': None, '防御': 0}
    if give_qq:
        if str(give_qq) == str(user_id):
            msg = "请不要偷自己刷成就！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await rob_stone.finish()

        user_2 = sql_message.get_user_message(give_qq)
        if user_2.root == "器师":
            msg = "对方职业无法被抢劫！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await rob_stone.finish()
        if user_2:
            if user_info.hp is None:
                # 判断用户气血是否为None
                sql_message.update_user_hp(user_id)
                user_info = sql_message.get_user_message(user_id)
            if user_2.hp is None:
                sql_message.update_user_hp(give_qq)
                user_2 = sql_message.get_user_message(give_qq)

            if user_2.hp <= user_2.exp / 10:
                time_2 = leave_harm_time(give_qq)
                msg = f"对方重伤藏匿了，无法抢劫！距离对方脱离生命危险还需要{time_2}分钟！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await rob_stone.finish()

            if user_info.hp <= user_info.exp / 10:
                time_msg = leave_harm_time(user_id)
                msg = f"重伤未愈，动弹不得！距离脱离生命危险还需要{time_msg}分钟！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await rob_stone.finish()
            impart_data_1 = xiuxian_impart.get_user_message(user_id)
            player1['user_id'] = user_info.user_id
            player1['道号'] = user_info.user_name
            player1['气血'] = user_info.hp
            player1['攻击'] = user_info.atk
            player1['真元'] = user_info.mp
            player1['会心'] = int(
                (0.01 + impart_data_1.impart_know_per if impart_data_1 is not None else 0) * 100)
            player1['爆伤'] = int(
                1.5 + impart_data_1.impart_burst_per if impart_data_1 is not None else 0)
            user_buff_data = UserBuffDate(user_id)
            user_armor_data = user_buff_data.get_user_armor_buff_data()
            if user_armor_data is not None:
                def_buff = int(user_armor_data['def_buff'])
            else:
                def_buff = 0
            player1['防御'] = def_buff

            impart_data_2 = xiuxian_impart.get_user_message(user_2.user_id)
            player2['user_id'] = user_2.user_id
            player2['道号'] = user_2.user_name
            player2['气血'] = user_2.hp
            player2['攻击'] = user_2.atk
            player2['真元'] = user_2.mp
            player2['会心'] = int(
                (0.01 + impart_data_2.impart_know_per if impart_data_2 is not None else 0) * 100)
            player2['爆伤'] = int(
                1.5 + impart_data_2.impart_burst_per if impart_data_2 is not None else 0)
            user_buff_data = UserBuffDate(user_2.user_id)
            user_armor_data = user_buff_data.get_user_armor_buff_data()
            if user_armor_data is not None:
                def_buff = int(user_armor_data['def_buff'])
            else:
                def_buff = 0
            player2['防御'] = def_buff

            result, victor = OtherSet().player_fight(player1, player2)
            await send_forward_msg(bot, event, '决斗场', bot.self_id, result)
            if victor == player1['道号']:
                foe_stone = user_2.stone
                if foe_stone > 0:
                    sql_message.update_ls(user_id, int(foe_stone * 0.1), 1)
                    sql_message.update_ls(give_qq, int(foe_stone * 0.1), 2)
                    exps = int(user_2.exp * 0.005)
                    sql_message.update_exp(user_id, exps)
                    sql_message.update_j_exp(give_qq, exps / 2)
                    msg = "大战一番，战胜对手，获取灵石{}枚，修为增加{}，对手修为减少{}".format(int(foe_stone * 0.1), exps, exps / 2)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await rob_stone.finish()
                else:
                    exps = int(user_2.exp * 0.005)
                    sql_message.update_exp(user_id, exps)
                    sql_message.update_j_exp(give_qq, exps / 2)
                    msg = "大战一番，战胜对手，结果对方是个穷光蛋，修为增加{}，对手修为减少{}".format(exps, exps / 2)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await rob_stone.finish()

            elif victor == player2['道号']:
                mind_stone = user_info.stone
                if mind_stone > 0:
                    sql_message.update_ls(user_id, int(mind_stone * 0.1), 2)
                    sql_message.update_ls(give_qq, int(mind_stone * 0.1), 1)
                    exps = int(user_info.exp * 0.005)
                    sql_message.update_j_exp(user_id, exps)
                    sql_message.update_exp(give_qq, exps / 2)
                    msg = "大战一番，被对手反杀，损失灵石{}枚，修为减少{}，对手获取灵石{}枚，修为增加{}".format(int(mind_stone * 0.1), exps,
                                                                              int(mind_stone * 0.1), exps / 2)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await rob_stone.finish()
                else:
                    exps = int(user_info.exp * 0.005)
                    sql_message.update_j_exp(user_id, exps)
                    sql_message.update_exp(give_qq, exps / 2)
                    msg = "大战一番，被对手反杀，修为减少{}，对手修为增加{}".format(exps, exps / 2)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                    else:
                        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                    await rob_stone.finish()

            else:
                msg = "发生错误！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await rob_stone.finish()

        else:
            msg = "没有对方的信息！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await rob_stone.finish()


@restate.handle(parameterless=[Cooldown(at_sender=True)])
async def restate_(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """重置用户状态。
    单用户：重置状态@xxx
    多用户：重置状态"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await steal_stone.finish()
    give_qq = None  # 艾特的时候存到这里
    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")
    if give_qq:
        sql_message.restate(give_qq)
        msg = '{}用户信息重置成功！'.format(give_qq)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await restate.finish()
    else:
        sql_message.restate()
        msg = '所有用户信息重置成功！'
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await restate.finish()


@open_xiuxian.handle()
async def open_xiuxian_(bot: Bot, event: GroupMessageEvent):
    """群修仙开关配置"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    group_msg = str(event.message)
    group_id = str(event.group_id)
    if "启用" in group_msg:
        JsonConfig().write_data(1, group_id)  # 添加
        msg = "当前群聊修仙模组已启用！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await open_xiuxian.finish()

    elif "禁用" in group_msg:
        JsonConfig().write_data(2, group_id)  # 删除
        msg = "当前群聊修仙模组已禁用！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await open_xiuxian.finish()
    else:
        msg = "指令错误，请输入：启用修仙功能/禁用修仙功能"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await open_xiuxian.finish()


@xiuxian_updata_level.handle(parameterless=[Cooldown(at_sender=True)])
async def xiuxian_updata_level_(bot: Bot, event: GroupMessageEvent):
    """将修仙1的境界适配到修仙2"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await xiuxian_updata_level.finish()
    level_dict={
        "练气境":"搬血境",
        "筑基境":"洞天境",
        "结丹境":"化灵境",
        "元婴境":"铭纹境",
        "化神境":"列阵境",
        "炼虚境":"尊者境",
        "合体境":"神火境",
        "大乘境":"真一境",
        "渡劫境":"圣祭境",
        "半步真仙":"天神境中期",
        "真仙境":"虚道境",
        "金仙境":"斩我境",
        "太乙境":"遁一境"
    }
    level = user_info.level
    user_id = user_info.user_id
    if level == "半步真仙":
        level = "天神境中期"
    else:
        try:
            level = level_dict.get(level[:3]) + level[-2:]
        except:
            level = level
    sql_message.updata_level(user_id=user_id,level_name=level)
    msg = '境界适配成功成功！'
    if XiuConfig().img:
        pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
    else:
        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
    await xiuxian_updata_level.finish()