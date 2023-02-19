from pathlib import Path

DATABASE = Path() / "data" / "xiuxian"


class IMPART_BUFF_CONFIG:
    def __init__(self):
        self.sql_table = ["xiuxian_impart"]
        # 数据库字段
        self.sql_table_impart_buff = ["id", "user_id", "impart_hp_per",
                                      "impart_atk_per", "impart_mp_per",
                                      "impart_exp_up", "boss_atk",
                                      "impart_know_per", "impart_burst_per",
                                      "impart_mix_per", "impart_reap_per",
                                      "impart_two_exp", "stone_num"]


config_impart = IMPART_BUFF_CONFIG()
