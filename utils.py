from aiocqhttp import MessageSegment
from .xiuxian_config import XiuConfig
from .xiuxian2_handle import XiuxianDateManage
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GroupMessageEvent
)
import json
import math
import datetime
import unicodedata
from nonebot.params import Depends
from base64 import b64encode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from wcwidth import wcwidth
import os
from .data_source import jsondata
from pathlib import Path

sql_message = XiuxianDateManage()  # sql类
boss_img_path = Path() / "data" / "xiuxian" / "boss_img"


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        if isinstance(obj, int):
            return int(obj)
        elif isinstance(obj, float):
            return float(obj)
        else:
            return super(MyEncoder, self).default(obj)


def check_user_type(user_id, need_type):
    """
    :说明: `check_user_type`
    > 匹配用户状态，返回是否状态一致
    :返回参数:
      * `isType: 是否一致
      * `msg: 消息体
    """
    isType = False
    msg = ''
    user_cd_message = sql_message.get_user_cd(user_id)
    if user_cd_message is None:
        user_type = 0
    else:
        user_type = user_cd_message.type

    if user_type == need_type:  # 状态一致
        isType = True
    else:
        if user_type == 1:
            msg = "道友现在在闭关呢，小心走火入魔！"

        elif user_type == 2:
            msg = "道友现在在做悬赏令呢，小心走火入魔！"

        elif user_type == 3:
            msg = "道友现在正在秘境中，分身乏术！"

        elif user_type == 0:
            msg = "道友现在什么都没干呢~"

    return isType, msg


def check_user(event: GroupMessageEvent):
    """
    判断用户信息是否存在
    :返回参数:
      * `isUser: 是否存在
      * `user_info: 用户
      * `msg: 消息体
    """

    isUser = False
    user_id = event.get_user_id()
    user_info = sql_message.get_user_message(user_id)
    if user_info is None:
        msg = "修仙界没有道友的信息，请输入【我要修仙】加入！"
    else:
        isUser = True
        msg = ''

    return isUser, user_info, msg


async def send_forward_msg(
        bot: Bot,
        event: MessageEvent,
        name: str,  # 转发的用户名称
        uin: str,  # qq
        msgs: list  # 转发内容
):
    """合并消息转发"""

    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    if isinstance(event, GroupMessageEvent):
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=messages
        )
    else:
        await bot.call_api(
            "send_private_forward_msg", user_id=event.user_id, messages=messages
        )


async def send_forward_msg_list(
        bot: Bot,
        event: MessageEvent,
        messages: list,  # 格式[*dict] 例[*{"type": "node", "data": {"name": name, "uin": uin, "content": msg}}]
):
    """
    合并消息转发
    区分人
    """

    if isinstance(event, GroupMessageEvent):
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=messages
        )
    else:
        await bot.call_api(
            "send_private_forward_msg", user_id=event.user_id, messages=messages
        )


class Txt2Img:
    """保存帮助信息为图片文件
    插件copy为nonebot-plugin-txt2img
    git:https://github.com/mobyw/nonebot-plugin-txt2img"""

    def __init__(self, size=30):
        self.font_family = str(jsondata.FONT_FILE)
        self.user_font_size = int(size * 1.5)
        self.lrc_font_size = int(size)
        self.line_space = int(size)
        self.lrc_line_space = int(size / 2)
        self.stroke = 5
        self.share_img_width = 1080

    def wrap(self, string):
        max_width = int(1850 / self.lrc_font_size)
        temp_len = 0
        result = ''
        for ch in string:
            result += ch
            temp_len += wcwidth(ch)
            if ch == '\n':
                temp_len = 0
            if temp_len > max_width:
                temp_len = 0
                result += '\n'
        result = result.rstrip()
        return result

    def save(self, title, lrc, boss_name=""):
        """MI Note"""
        title = unicodedata.normalize('NFKC', title)
        lrc = unicodedata.normalize('NFKC', lrc)
        border_color = (220, 211, 196)
        text_color = (125, 101, 89)

        out_padding = 30
        padding = 45
        banner_size = 20

        user_font = ImageFont.truetype(self.font_family, self.user_font_size)
        lyric_font = ImageFont.truetype(self.font_family, self.lrc_font_size)

        if title == ' ':
            title = ''
        lrc = self.wrap(lrc)

        if lrc.find("\n") > -1:
            lrc_rows = len(lrc.split("\n"))
        else:
            lrc_rows = 1

        w = self.share_img_width

        if title:
            inner_h = (
                    padding * 2
                    + self.user_font_size
                    + self.line_space
                    + self.lrc_font_size * lrc_rows
                    + (lrc_rows - 1) * self.lrc_line_space
            )
        else:
            inner_h = (
                    padding * 2
                    + self.lrc_font_size * lrc_rows
                    + (lrc_rows - 1) * self.lrc_line_space
            )

        h = out_padding * 2 + inner_h

        out_img = Image.new(mode="RGB", size=(w, h), color=(255, 255, 255))
        draw = ImageDraw.Draw(out_img)

        mi_img = Image.open(jsondata.BACKGROUND_FILE)
        mi_banner = Image.open(jsondata.BANNER_FILE).resize(
            (banner_size, banner_size), resample=3
        )

        # add background
        for x in range(int(math.ceil(h / 100))):
            out_img.paste(mi_img, (0, x * 100))

        # add border
        def draw_rectangle(draw, rect, width):
            for i in range(width):
                draw.rectangle(
                    (rect[0] + i, rect[1] + i, rect[2] - i, rect[3] - i),
                    outline=border_color,
                )

        draw_rectangle(
            draw, (out_padding, out_padding, w - out_padding, h - out_padding), 2
        )

        # add banner
        out_img.paste(mi_banner, (out_padding, out_padding))
        out_img.paste(
            mi_banner.transpose(Image.FLIP_TOP_BOTTOM),
            (out_padding, h - out_padding - banner_size + 1),
        )
        out_img.paste(
            mi_banner.transpose(Image.FLIP_LEFT_RIGHT),
            (w - out_padding - banner_size + 1, out_padding),
        )
        out_img.paste(
            mi_banner.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM),
            (w - out_padding - banner_size + 1, h - out_padding - banner_size + 1),
        )

        if title:
            user_w, user_h = ImageDraw.Draw(
                Image.new(mode="RGB", size=(1, 1))
            ).textsize(title, font=user_font, spacing=self.line_space)
            draw.text(
                ((w - user_w) // 2, out_padding + padding),
                title,
                font=user_font,
                fill=text_color,
                spacing=self.line_space,
            )
            draw.text(
                (
                    out_padding + padding,
                    out_padding + padding + self.user_font_size + self.line_space,
                ),
                lrc,
                font=lyric_font,
                fill=text_color,
                spacing=self.lrc_line_space,
            )
        else:
            draw.text(
                (out_padding + padding, out_padding + padding),
                lrc,
                font=lyric_font,
                fill=text_color,
                spacing=self.lrc_line_space,
            )
        if boss_name:
            path_ = boss_img_path / f'{boss_name}.png'
            if os.path.exists(path_):
                boss_img = Image.open(path_)
                base_cc = boss_img.height / h
                boss_img_w = int(boss_img.width / base_cc)
                boss_img_h = int(boss_img.height / base_cc)
                boss_img = boss_img.resize((int(boss_img_w), int(boss_img_h)), Image.ANTIALIAS)
                out_img.paste(
                    boss_img,
                    (int(w - boss_img_w), int(h - boss_img_h)),
                    boss_img
                )
        return self.img2b64(out_img)

    def img2b64(self, out_img) -> str:
        """ image to base64 """
        buf = BytesIO()
        out_img.save(buf, format="PNG")
        base64_str = "base64://" + b64encode(buf.getvalue()).decode()
        return base64_str


async def get_msg_pic(msg, title=' ', font_size=52, boss_name=""):
    img = Txt2Img(font_size)
    pic = img.save(title, msg, boss_name)
    return pic

async def get_msg_pic2(msg, title=' ', font_size=52, boss_name=""):
    """_summary_
        msg2pic if XiuConfig().img
    Args:
        msg (_type_): _description_
        title (str, optional): _description_. Defaults to ' '.
        font_size (int, optional): _description_. Defaults to 52.
        boss_name (str, optional): _description_. Defaults to "".

    Returns:
        _type_: _description_
    """
    if XiuConfig().img:
        img = Txt2Img(font_size)
        pic = img.save(title, msg, boss_name)
        pic = MessageSegment.image(pic)
        return pic

def CommandObjectID() -> int:
    """
    根据消息事件的类型获取对象id
    私聊->用户id
    群聊->群id
    频道->子频道id
    :return: 对象id
    """

    def _event_id(event):
        if event.message_type == 'private':
            return event.user_id
        elif event.message_type == 'group':
            return event.group_id
        elif event.message_type == 'guild':
            return event.channel_id

    return Depends(_event_id)


def number_to(num):
    '''
    递归实现，精确为最大单位值 + 小数点后一位
    '''
    def strofsize(num, level):
        if level >= 2:
            return num, level
        elif num >= 10000:
            num /= 10000
            level += 1
            return strofsize(num, level)
        else:
            return num, level
    units = ['', '万', '亿']
    num, level = strofsize(num, 0)
    if level > len(units):
        level -= 1
    return '{}{}'.format(round(num, 1), units[level])


