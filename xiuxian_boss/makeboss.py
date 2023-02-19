import random
from ..xiuxian2_handle import XiuxianDateManage
from .bossconfig import get_config

config = get_config()
JINGJIEEXP = {  # 数值为中期和圆满的平均值
    "搬血境": [1000, 2000, 3000],
    "洞天境": [6000, 8000.10000],
    "化灵境": [30000, 60000, 90000],
    "铭纹境": [144000, 160000, 176000],
    "列阵境": [352000, 284000, 416000],
    "尊者境": [832000, 896000, 960000],
    "神火境": [1920000, 2048000, 2176000],
    "真一境": [4352000, 4608000, 4864000],
    "圣祭境": [9728000, 12348000, 14968000],
    "天神境": [30968000, 35968000, 40968000],
    "虚道境": [60968000, 70968000, 80968000],
    "斩我境": [120968000, 140968000, 160968000],
    "遁一境": [321936000, 450710400, 579484800],
    "至尊境": [1158969600, 1622557440, 2086145280],
    "真仙境": [4172290560, 5841206784, 7510123008],
    "仙王境": [15020246016, 21028344422, 27036442828],
    "准帝境": [54072885657, 75702039920, 97331194180],
    "仙帝境": [194662388360, 272527343704, 350392299048],
    "祭道之上": [350392299048, 650392299048, 950392299048],
}

jinjie_list = [k for k, v in JINGJIEEXP.items()]
sql_message = XiuxianDateManage()  # sql类


def createboss():
    top_user_info = sql_message.get_top1_user()
    top_user_level = top_user_info.level
    if top_user_level == "祭道之上":
        level = top_user_level[:4]
    else:
        level = top_user_level[:3]
    boss_jj = random.choice(jinjie_list[:jinjie_list.index(level) + 1])

    bossinfo = get_boss_exp(boss_jj)
    bossinfo['name'] = random.choice(config["Boss名字"])
    bossinfo['jj'] = boss_jj
    bossinfo['stone'] = random.choice(config["Boss灵石"][boss_jj])
    return bossinfo


def get_boss_exp(boss_jj):
    bossexp = random.choice(JINGJIEEXP[boss_jj])
    bossinfo = {
        '气血': bossexp * config["Boss倍率"]["气血"],
        '总血量': bossexp * config["Boss倍率"]["气血"],
        '真元': bossexp * config["Boss倍率"]["真元"],
        '攻击': int(bossexp * config["Boss倍率"]["攻击"])
    }
    return bossinfo


JINGJIEEXP_root = {  # 数值为中期和圆满的平均值
    "搬血境": [1000, 2000, 3000],
    "洞天境": [6000, 8000.10000],
    "化灵境": [30000, 60000, 90000],
    "铭纹境": [144000, 160000, 176000],
    "列阵境": [352000, 284000, 416000],
    "尊者境": [832000, 896000, 960000]
}


def createboss_root():
    boss_jj = random.choice(list(JINGJIEEXP_root.keys()))
    bossinfo = get_boss_exp_root(boss_jj)
    bossinfo['name'] = random.choice(config["Boss名字"])
    bossinfo['jj'] = boss_jj
    bossinfo['stone'] = random.choice(config["Boss灵石"][boss_jj])
    return bossinfo


def get_boss_exp_root(boss_jj):
    bossexp = random.choice(JINGJIEEXP_root[boss_jj])
    bossinfo = {
        '气血': bossexp * config["Boss倍率"]["气血"],
        '总血量': bossexp * config["Boss倍率"]["气血"],
        '真元': bossexp * config["Boss倍率"]["真元"],
        '攻击': int(bossexp * config["Boss倍率"]["攻击"])
    }
    return bossinfo
