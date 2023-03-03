from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GROUP,
    GroupMessageEvent,
    MessageSegment,
)
from ..lay_out import assign_bot, Cooldown
from ..xiuxian2_handle import XiuxianDateManage, OtherSet
from ..data_source import jsondata
from .draw_user_info import draw_user_info_img
from ..utils import check_user, get_msg_pic, number_to
from ..read_buff import UserBuffDate
from ..xiuxian_config import XiuConfig


xiuxian_message = on_command("我的修仙信息", aliases={"我的存档"}, priority=23, permission=GROUP, block=True)
sql_message = XiuxianDateManage()  # sql类


@xiuxian_message.handle(parameterless=[Cooldown(cd_time=XiuConfig().user_info_cd, at_sender=True)])
async def xiuxian_message_(bot: Bot, event: GroupMessageEvent):
    """我的修仙信息"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await xiuxian_message.finish()
    user_id = user_info.user_id
    user_info = sql_message.get_user_real_info(user_id)
    user_name = user_info.user_name
    if user_name:
        pass
    else:
        user_name = "无名氏(发送改名+道号更新)"

    level_rate = sql_message.get_root_rate(user_info.root_type)  # 灵根倍率
    realm_rate = jsondata.level_data()[user_info.level]["spend"]  # 境界倍率
    sect_id = user_info.sect_id
    if sect_id:
        sect_info = sql_message.get_sect_info(sect_id)
        sectmsg = sect_info.sect_name
        sectzw = jsondata.sect_config_data()[f"{user_info.sect_position}"]["title"]
    else:
        sectmsg = '无宗门'
        sectzw = '无'

    # 判断突破的修为
    list_all = len(OtherSet().level) - 1
    now_index = OtherSet().level.index(user_info.level)
    if list_all == now_index:
        exp_meg = "位面至高"
    else:
        is_updata_level = OtherSet().level[now_index + 1]
        need_exp = sql_message.get_level_power(is_updata_level)
        get_exp = need_exp - user_info.exp
        if get_exp > 0:
            exp_meg = "还需{}修为可突破！".format(number_to(get_exp))
        else:
            exp_meg = "可突破！"

    user_buff_data = UserBuffDate(user_id)
    user_main_buff_date = user_buff_data.get_user_main_buff_data()
    user_sec_buff_date = user_buff_data.get_user_sec_buff_data()
    user_weapon_data = user_buff_data.get_user_weapon_data()
    user_armor_data = user_buff_data.get_user_armor_buff_data()
    main_buff_name = '无'
    sec_buff_name = '无'
    weapon_name = '无'
    armor_name = '无'
    if user_main_buff_date is not None:
        main_buff_name = f"{user_main_buff_date['name']}({user_main_buff_date['level']})"
    if user_sec_buff_date is not None:
        sec_buff_name = f"{user_sec_buff_date['name']}({user_sec_buff_date['level']})"
    if user_weapon_data is not None:
        weapon_name = f"{user_weapon_data['name']}({user_weapon_data['level']})"
    if user_armor_data is not None:
        armor_name = f"{user_armor_data['name']}({user_armor_data['level']})"

    DETAIL_MAP = {
        '道号': f'{user_name}',
        '境界': f'{user_info.level}',
        '修为': f'{number_to(user_info.exp)}',
        '灵石': f'{user_info.stone}',
        '战力': f'{number_to(int(user_info.exp * level_rate * realm_rate))}',
        '灵根': f'{user_info.root}({user_info.root_type}+{int(level_rate * 100)}%)',
        '突破状态': f'{exp_meg}概率：{jsondata.level_rate_data()[user_info.level] + int(user_info.level_up_rate)}%',
        '攻击力': f'{number_to(user_info.atk)}，攻修等级{user_info.atkpractice}级',
        '所在宗门': sectmsg,
        '宗门职位': sectzw,
        '主修功法': main_buff_name,
        '副修神通': sec_buff_name,
        "法器": weapon_name,
        "防具": armor_name,
    }
    if XiuConfig().user_info_image:
        img_res = await draw_user_info_img(user_id, DETAIL_MAP)
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(img_res))
        await xiuxian_message.finish()
    else:
        msg = f"""{user_name}道友的信息
灵根为：{user_info.root}({user_info.root_type}+{int(level_rate * 100)}%)
当前境界：{user_info.level}(境界+{int(realm_rate * 100)}%)
当前灵石：{user_info.stone}
当前修为：{user_info.exp}(修炼效率+{int((level_rate * realm_rate) * 100)}%)
突破状态：{exp_meg}
你的战力为：{int(user_info.exp * level_rate * realm_rate)}"""
        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await xiuxian_message.finish()
