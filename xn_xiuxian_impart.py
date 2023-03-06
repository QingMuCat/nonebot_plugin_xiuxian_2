import sqlite3
from collections import namedtuple
from pathlib import Path
from nonebot.log import logger
from .xn_xiuxian_impart_config import config_impart
from .xiuxian_config import XiuConfig
from .xiuxian2_handle import XiuxianDateManage
from . import DRIVER
from .data_source import jsondata
from .read_buff import UserBuffDate

sql_message = XiuxianDateManage()  # sql类

DATABASE_IMPARTBUFF = Path() / "data" / "xiuxian"

impart_buff = namedtuple("xiuxian_impart",
                         ["id", "user_id", "impart_hp_per", "impart_atk_per", "impart_mp_per", "impart_exp_up",
                          "boss_atk", "impart_know_per", "impart_burst_per", "impart_mix_per", "impart_reap_per",
                          "impart_two_exp", "stone_num", "exp_day", "wish"])

num = "123451234"


class XIUXIAN_IMPART_BUFF:
    global num
    _instance = {}
    _has_init = {}

    def __new__(cls):
        if cls._instance.get(num) is None:
            cls._instance[num] = super(XIUXIAN_IMPART_BUFF, cls).__new__(cls)
        return cls._instance[num]

    def __init__(self):
        if not self._has_init.get(num):
            self._has_init[num] = True
            self.database_path = DATABASE_IMPARTBUFF
            if not self.database_path.exists():
                self.database_path.mkdir(parents=True)
                self.database_path /= "xiuxian_impart.db"
                self.conn = sqlite3.connect(self.database_path)
                # self._create_file()
            else:
                self.database_path /= "xiuxian_impart.db"
                self.conn = sqlite3.connect(self.database_path)
            logger.info(f"xiuxian_impart数据库已连接!")
            self._check_data()

    def close(self):
        self.conn.close()
        logger.info(f"xiuxian_impart数据库关闭!")

    def _create_file(self) -> None:
        """创建数据库文件"""
        c = self.conn.cursor()
        c.execute('''CREATE TABLE xiuxian_impart
                           (NO            INTEGER PRIMARY KEY UNIQUE,
                           USERID         TEXT     ,
                           level          INTEGER  ,
                           root           INTEGER
                           );''')
        c.execute('''''')
        c.execute('''''')
        self.conn.commit()

    def _check_data(self):
        """检查数据完整性"""
        c = self.conn.cursor()

        for i in config_impart.sql_table:
            if i == "xiuxian_impart":
                try:
                    c.execute(f"select count(1) from {i}")
                except sqlite3.OperationalError:
                    c.execute("""CREATE TABLE "xiuxian_impart" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" integer DEFAULT 0,
    "impart_hp_per" integer DEFAULT 0,
    "impart_atk_per" integer DEFAULT 0,
    "impart_mp_per" integer DEFAULT 0,
    "impart_exp_up" integer DEFAULT 0,
    "boss_atk" integer DEFAULT 0,
    "impart_know_per" integer DEFAULT 0,
    "impart_burst_per" integer DEFAULT 0,
    "impart_mix_per" integer DEFAULT 0,
    "impart_reap_per" integer DEFAULT 0,
    "impart_two_exp" integer DEFAULT 0,
    "stone_num" integer DEFAULT 0,
    "exp_day" integer DEFAULT 0,
    "wish" integer DEFAULT 0
    );""")

        for s in config_impart.sql_table_impart_buff:
            try:
                c.execute(f"select {s} from xiuxian_impart")
            except sqlite3.OperationalError:
                sql = f"ALTER TABLE xiuxian_impart ADD COLUMN {s} integer DEFAULT 0;"
                print(sql)
                logger.info(f"xiuxian_impart数据库核对成功!")
                c.execute(sql)

        self.conn.commit()

    @classmethod
    def close_dbs(cls):
        XIUXIAN_IMPART_BUFF().close()

    def create_user(self, user_id):
        """校验用户是否存在"""
        cur = self.conn.cursor()
        sql = f"select * from xiuxian_impart where user_id=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return False
        else:
            return True

    def _create_user(self, user_id: str) -> None:
        """在数据库中创建用户并初始化"""
        if self.create_user(user_id):
            pass
        else:
            c = self.conn.cursor()
            sql = f"INSERT INTO xiuxian_impart (user_id, impart_hp_per, impart_atk_per, impart_mp_per, impart_exp_up ,boss_atk,impart_know_per,impart_burst_per,impart_mix_per,impart_reap_per,impart_two_exp,stone_num,exp_day,wish) VALUES(?, 0, 0, 0, 0 ,0, 0, 0, 0, 0 ,0 ,0 ,0, 0) "
            c.execute(sql, (user_id,))
            self.conn.commit()

    def get_user_message(self, user_id):
        """根据USER_ID获取用户impart_buff信息"""
        cur = self.conn.cursor()
        sql = f"select * from xiuxian_impart where user_id=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return None
        else:
            return impart_buff(*result)

    def update_impart_hp_per(self, impart_num, user_id):
        """更新impart_hp_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_hp_per=? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def add_impart_hp_per(self, impart_num, user_id):
        """add impart_hp_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_hp_per=impart_hp_per+? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def update_impart_atk_per(self, impart_num, user_id):
        """更新impart_atk_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_atk_per=? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def add_impart_atk_per(self, impart_num, user_id):
        """add  impart_atk_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_atk_per=impart_atk_per+? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def update_impart_mp_per(self, impart_num, user_id):
        """impart_mp_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_mp_per=? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def add_impart_mp_per(self, impart_num, user_id):
        """add impart_mp_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_mp_per=impart_mp_per+? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def update_impart_exp_up(self, impart_num, user_id):
        """impart_exp_up"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_exp_up=? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def add_impart_exp_up(self, impart_num, user_id):
        """add impart_exp_up"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_exp_up=impart_exp_up+? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def update_boss_atk(self, impart_num, user_id):
        """boss_atk"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET boss_atk=? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def add_boss_atk(self, impart_num, user_id):
        """add boss_atk"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET boss_atk=boss_atk+? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def update_impart_know_per(self, impart_num, user_id):
        """impart_know_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_know_per=? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def add_impart_know_per(self, impart_num, user_id):
        """add impart_know_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_know_per=impart_know_per+? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def update_impart_burst_per(self, impart_num, user_id):
        """impart_burst_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_burst_per=? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def add_impart_burst_per(self, impart_num, user_id):
        """add impart_burst_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_burst_per=impart_burst_per+? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def update_impart_mix_per(self, impart_num, user_id):
        """impart_mix_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_mix_per=? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def add_impart_mix_per(self, impart_num, user_id):
        """add impart_mix_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_mix_per=impart_mix_per+? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def update_impart_reap_per(self, impart_num, user_id):
        """impart_reap_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_reap_per=? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def add_impart_reap_per(self, impart_num, user_id):
        """add impart_reap_per"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_reap_per=impart_reap_per+? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def update_impart_two_exp(self, impart_num, user_id):
        """impart_two_exp"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_two_exp=? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def add_impart_two_exp(self, impart_num, user_id):
        """add impart_two_exp"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET impart_two_exp=impart_two_exp+? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def update_impart_wish(self, impart_num, user_id):
        """update impart_wish"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET wish=? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def add_impart_wish(self, impart_num, user_id):
        """add impart_wish"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET wish=wish+? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def update_stone_num(self, impart_num, user_id, type_):
        """impart_stone_num"""
        if type_ == 1:
            cur = self.conn.cursor()
            sql = f"UPDATE xiuxian_impart SET stone_num=stone_num+? WHERE user_id=?"
            cur.execute(sql, (impart_num, user_id))
            self.conn.commit()
            return True
        if type_ == 2:
            cur = self.conn.cursor()
            sql = f"UPDATE xiuxian_impart SET stone_num=stone_num-? WHERE user_id=?"
            cur.execute(sql, (impart_num, user_id))
            self.conn.commit()
            return True

    def update_impart_stone_all(self, impart_stone):
        """所有用户增加结晶"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET stone_num=stone_num+?"
        cur.execute(sql, (impart_stone,))
        self.conn.commit()

    def add_impart_exp_day(self, impart_num, user_id):
        """add  impart_exp_day"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET exp_day=exp_day+? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True

    def use_impart_exp_day(self, impart_num, user_id):
        """use  impart_exp_day"""
        cur = self.conn.cursor()
        sql = f"UPDATE xiuxian_impart SET exp_day=exp_day-? WHERE user_id=?"
        cur.execute(sql, (impart_num, user_id))
        self.conn.commit()
        return True


def leave_harm_time(user_id):
    hp_speed = 25
    user_mes = sql_message.get_user_message(user_id)  # 获取用户信息
    level = user_mes.level
    level_rate = sql_message.get_root_rate(user_mes.root_type)  # 灵根倍率
    realm_rate = jsondata.level_data()[level]["spend"]  # 境界倍率
    user_buff_data = UserBuffDate(user_id)
    mainbuffdata = UserBuffDate(user_id).get_user_main_buff_data()
    mainbuffratebuff = mainbuffdata['ratebuff'] if mainbuffdata != None else 0  # 功法修炼倍率
    try:
        time = int(((user_mes.exp / 10) - user_mes.hp) / ((XiuConfig().closing_exp * level_rate * realm_rate * (
                    1 + mainbuffratebuff)) * hp_speed))
    except:
        time = "无穷大"
    return time


async def impart_check(user_id):
    if XIUXIAN_IMPART_BUFF().get_user_message(user_id) is None:
        XIUXIAN_IMPART_BUFF()._create_user(user_id)
        return XIUXIAN_IMPART_BUFF().get_user_message(user_id)
    else:
        return XIUXIAN_IMPART_BUFF().get_user_message(user_id)


@DRIVER.on_shutdown
async def close_db():
    XIUXIAN_IMPART_BUFF().close()
