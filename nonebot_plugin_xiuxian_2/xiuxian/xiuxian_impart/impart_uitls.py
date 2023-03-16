import numpy
from ..xn_xiuxian_impart import XIUXIAN_IMPART_BUFF
from .impart_data import impart_data_json

xiuxian_impart = XIUXIAN_IMPART_BUFF()


def random_int():
    return numpy.random.randint(low=0, high=10000, size=None, dtype='l')


# 抽卡概率来自https://www.bilibili.com/read/cv10468091
# 角色抽卡概率
def character_probability(count):
    count += 1
    if count <= 73:
        ret = 60
    else:
        ret = 60 + 600 * (count - 73)
    return ret


def get_rank(user_id):
    impart_data = xiuxian_impart.get_user_message(user_id)
    value = random_int()
    num = int(impart_data.wish)
    for x in range(num, num + 10):
        index_5 = character_probability(x)
        if value <= index_5:
            return True
        if x >= 89:
            return True
    return False


async def impart_check(user_id):
    impart_data_json.find_user_impart(user_id)
    if xiuxian_impart.get_user_message(user_id) is None:
        xiuxian_impart._create_user(user_id)
        return xiuxian_impart.get_user_message(user_id)
    else:
        return xiuxian_impart.get_user_message(user_id)


async def re_impart_data(user_id):
    list_tp = impart_data_json.data_person_list(user_id)
    if list_tp is None:
        return False
    else:
        all_data = impart_data_json.data_all_()
        impart_two_exp = 0
        impart_exp_up = 0
        impart_atk_per = 0
        impart_hp_per = 0
        impart_mp_per = 0
        boss_atk = 0
        impart_know_per = 0
        impart_burst_per = 0
        impart_mix_per = 0
        impart_reap_per = 0
        for x in list_tp:
            if all_data[x]["type"] == "impart_two_exp":
                impart_two_exp = impart_two_exp + all_data[x]["vale"]
            elif all_data[x]["type"] == "impart_exp_up":
                impart_exp_up = impart_exp_up + all_data[x]["vale"]
            elif all_data[x]["type"] == "impart_atk_per":
                impart_atk_per = impart_atk_per + all_data[x]["vale"]
            elif all_data[x]["type"] == "impart_hp_per":
                impart_hp_per = impart_hp_per + all_data[x]["vale"]
            elif all_data[x]["type"] == "impart_mp_per":
                impart_mp_per = impart_mp_per + all_data[x]["vale"]
            elif all_data[x]["type"] == "boss_atk":
                boss_atk = boss_atk + all_data[x]["vale"]
            elif all_data[x]["type"] == "impart_know_per":
                impart_know_per = impart_know_per + all_data[x]["vale"]
            elif all_data[x]["type"] == "impart_burst_per":
                impart_burst_per = impart_burst_per + all_data[x]["vale"]
            elif all_data[x]["type"] == "impart_mix_per":
                impart_mix_per = impart_mix_per + all_data[x]["vale"]
            elif all_data[x]["type"] == "impart_reap_per":
                impart_reap_per = impart_reap_per + all_data[x]["vale"]
            else:
                pass
        xiuxian_impart.update_impart_two_exp(impart_two_exp, user_id)
        xiuxian_impart.update_impart_exp_up(impart_exp_up, user_id)
        xiuxian_impart.update_impart_atk_per(impart_atk_per, user_id)
        xiuxian_impart.update_impart_hp_per(impart_hp_per, user_id)
        xiuxian_impart.update_impart_mp_per(impart_mp_per, user_id)
        xiuxian_impart.update_boss_atk(boss_atk, user_id)
        xiuxian_impart.update_impart_know_per(impart_know_per, user_id)
        xiuxian_impart.update_impart_burst_per(impart_burst_per, user_id)
        xiuxian_impart.update_impart_mix_per(impart_mix_per, user_id)
        xiuxian_impart.update_impart_reap_per(impart_reap_per, user_id)
        return True
