try:
    import ujson as json
except ImportError:
    import json
from pathlib import Path

DATABASE = Path() / "data" / "xiuxian"

USERRANK = {
    '江湖好手': 56,
    '搬血境初期': 55,  # '练气境初期': 54,
    '搬血境中期': 54,
    '搬血境圆满': 53,
    '洞天境初期': 52,  # '筑基境初期': 51,
    '洞天境中期': 51,
    '洞天境圆满': 50,
    '化灵境初期': 49,  # '结丹境初期': 48,
    '化灵境中期': 48,
    '化灵境圆满': 47,
    '铭纹境初期': 46,  # '元婴境初期': 45,
    '铭纹境中期': 45,
    '铭纹境圆满': 44,
    '列阵境初期': 43,  # '化神境中期': 41,
    '列阵境中期': 42,
    '列阵境圆满': 41,
    '尊者境初期': 40,  # '炼虚境初期': 39,
    '尊者境中期': 39,
    '尊者境圆满': 38,
    '神火境初期': 37,  # '合体境初期': 36,
    '神火境中期': 36,
    '神火境圆满': 35,
    '真一境初期': 34,  # '大乘境初期': 33,
    '真一境中期': 33,
    '真一境圆满': 32,
    '圣祭境初期': 31,  # '渡劫境初期': 30,
    '圣祭境中期': 30,
    '圣祭境圆满': 29,
    '天神境初期': 28,  # '半步真仙': 37,
    '天神境中期': 27,
    '天神境圆满': 26,
    '虚道境初期': 25,  # '真仙境初期': 36,
    '虚道境中期': 24,
    '虚道境圆满': 23,
    '斩我境初期': 22,  # '金仙境初期': 33,
    '斩我境中期': 21,
    '斩我境圆满': 20,
    '遁一境初期': 19,  # '太乙境圆满': 28,
    '遁一境中期': 18,
    '遁一境圆满': 17,
    '至尊境初期': 16,
    '至尊境中期': 15,
    '至尊境圆满': 14,
    '真仙境初期': 13,
    '真仙境中期': 12,
    '真仙境圆满': 11,
    '仙王境初期': 10,
    '仙王境中期': 9,
    '仙王境圆满': 8,
    '准帝境初期': 7,
    '准帝境中期': 6,
    '准帝境圆满': 5,
    '仙帝境初期': 4,
    '仙帝境中期': 3,
    '仙帝境圆满': 2,
    '祭道之上': 1,
}


class XiuConfig:
    def __init__(self):
        self.sql_table = ["user_xiuxian", "user_cd", "sects", "back", "BuffInfo"]  # 数据库表校验
        self.sql_user_xiuxian = ["id", "user_id", "stone", "root",
                                 "root_type", "level", "power",
                                 "create_time", "is_sign", "exp",
                                 "user_name", "level_up_cd",
                                 "level_up_rate", "sect_id",
                                 "sect_position", "hp", "mp", "atk",
                                 "atkpractice", "sect_task", "sect_contribution",
                                 "sect_elixir_get", "blessed_spot_flag",
                                 "blessed_spot_name"]  # 数据库字段校验
        self.sql_sects = ["sect_id", "sect_name", "sect_owner", "sect_scale", "sect_used_stone", "sect_fairyland",
                          "sect_materials", "mainbuff", "secbuff", "elixir_room_level"]
        self.sql_buff = ["id", "user_id", "main_buff", "sec_buff", "faqi_buff", "fabao_weapon", "armor_buff",
                         "atk_buff", "blessed_spot"]
        self.sql_back = ["user_id", "goods_id", "goods_name", "goods_type", "goods_num", "create_time", "update_time",
                         "remake", "day_num", "all_num", "action_time", "state", "bind_num"]
        self.img = True
        self.user_info_image = True
        self.level = list(USERRANK.keys())
        self.user_info_cd = 60  # 我的存档冷却时间
        self.level_up_cd = 60  # 突破CD(分钟)
        self.closing_exp = 30  # 闭关每分钟获取的修为
        self.put_bot = []  # 接收消息qq,主qq，框架将只处理此qq的消息，
        self.main_bo = []  # 负责发送消息的qq
        self.shield_group = []  # 屏蔽的群聊
        self.layout_bot_dict = {

        }  
        # QQ所负责的群聊 #{群 ：bot}   其中 bot类型 []或str }
        self.sect_min_level = "铭纹境圆满"
        self.sect_create_cost = 5000000
        self.closing_exp_upper_limit = 1.5  # 闭关获取修为上限（例如：1.5 下个境界的修为数*1.5）
        self.level_punishment_floor = 1  # 突破失败扣除修为，惩罚下限（百分比）
        self.level_punishment_limit = 10  # 突破失败扣除修为，惩罚上限(百分比)
        self.level_up_probability = 0.3  # 突破失败增加当前境界突破概率的比例
        self.sign_in_lingshi_lower_limit = 200000  # 每日签到灵石下限
        self.sign_in_lingshi_upper_limit = 500000  # 每日签到灵石上限
        self.tou = 1000000  # 偷灵石惩罚
        self.tou_cd = 600  # 偷灵石cd/秒
        self.tou_lower_limit = 0.01  # 偷灵石下限(百分比)
        self.tou_upper_limit = 0.2  # 偷灵石上限(百分比)
        self.remake = 100000  # 重入仙途的消费
        self.del_boss_id = []  # 支持非管理员和超管天罚boss
        self.version = "xiuxian_2.1"


class JsonConfig:
    def __init__(self):
        self.config_jsonpath = DATABASE / "config.json"

    def read_data(self):
        """配置数据"""
        with open(self.config_jsonpath, 'r', encoding='utf-8') as e:
            data = json.load(e)
            return data

    def write_data(self, key, group_id=None):
        """
        说明：设置修仙开启或关闭
        参数：
            key: 群聊 1 为开启， 2为关闭,默认关闭
        """
        json_data = self.read_data()
        if key == 1:
            try:
                json_data['group'].append(group_id)
            except ValueError:
                print('加入数据失败')
                return False
        elif key == 2:
            try:
                json_data['group'].remove(group_id)
            except ValueError:
                print('删除数据失败')
                return False
        else:
            print('未知key')
            return False

        with open(self.config_jsonpath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
