from typing import List
import random
from ..xn_xiuxian_impart import XIUXIAN_IMPART_BUFF

xiuxian_impart = XIUXIAN_IMPART_BUFF()


def random_bullet() -> List[int]:
    """
    随机子弹排列
    """
    bullet_lst = [0, 0, 0, 0, 0, 0]
    for i in random.sample([0, 1, 2, 3, 4, 5], 1):
        bullet_lst[i] = 1
    return bullet_lst


async def impart_pk_check(user_id):
    if xiuxian_impart.get_user_message(user_id) is None:
        xiuxian_impart._create_user(user_id)
        return xiuxian_impart.get_user_message(user_id)
    else:
        return xiuxian_impart.get_user_message(user_id)


msg_pass = {
    0: ["向对手挥出了一掌\n", "向对手迸发出一波剑气\n", "向对手发动了法宝\n"],
    1: ["受到了对手的攻击，防御被攻破了\n", "受到了对手的攻击，防御被攻破了\n", "受到了对手的攻击，防御被攻破了\n"],
    2: ["整顿了一下剩下的防具，重整了姿势\n", "整顿了一下剩下的法宝，重整了姿势\n", "整顿了一下真气，重整了姿势\n"],
    3: ["感受到了天地间的动荡，貌似有奇遇将要出现\n", "前方空间发生了变化，是福是祸，犹未可知\n"],
    4: ["奇遇的降临让你获得了荒天帝的精血传承，一股力量涌入，头脑中突然符文密布，随机迸发了出来，环绕着你的身体。"
        "随机你只是在心中默念了一下符文，随即乾坤颠覆，日月无光，山河颓势尽显，虚神界的境界压制瞬间就被你打破了，"
        "随后你筋疲力尽意识陷入了模糊\n", "奇遇的降临让你得到了一片柳枝，一股力量涌入，头脑中突然符文密布，"
                            "随机迸发了出来，环绕者你的身体。随机你只是在心中默念了一下符文，随即乾坤颠覆，日月无光，山河颓势尽显，"
                            "虚神界的境界压制瞬间就被你打破了，随后你筋疲力尽意识陷入了模糊\n"]
}
msg_died = {
    0: ["向对手挥出了一掌，结果对手一个接化发，败了\n", "向对手迸发出一波剑气，结果对手一个接化发，败了\n", "向对手发动了法宝，结果对手一个接化发，败了\n"],
    1: ["受到了对手的攻击，防具碎了，没有招架住，败了\n", "受到了对手的攻击，法宝碎了，没有招架住，败了\n", "受到了对手的攻击，肉身抗了下来，没有招架住，败了\n"],
    2: ["整顿了一下剩下的防具，结果力不从心，败了\n", "整顿了一下剩下的法宝，结果力不从心，败了\n", "整顿了一下真气，结果力不从心，败了\n"],
    3: ["感受到了天地间的动荡，貌似有奇遇将要出现，被卷入其中，败了\n", "前方空间发生了变化，被卷入其中，败了\n"],
    4: ["空间破碎，只听见一句“仙之巅，傲世间，有我安澜便有天。”你便被一只手掌抓入了空间裂隙中，败了\n", "奇遇降临，你本想向前去查看，但你却在看见裂隙中隐隐约约中"
                                                            "看见了那位的身影，你一股热血涌入心头，离开时虚神界，败了\n"],
    5: ["见空间不稳定，随机便用出了空间秘术，准备踏空间而去，但你进入空间裂隙之后，却发现裂隙在一点点破碎，仿佛将要不存在了一样，你顿时就好像明白了什么，但转眼间"
        "便消亡了，败了\n", "见空间不稳定，随机便用出了时间秘术，准备逆时间长河而去，但你进入时间裂隙之后，却发现裂隙在一点点破碎，仿佛将要不存在了一样，你顿时就"
                    "好像明白了什么，但转眼间便消亡了，败了\n"]
}


async def impart_pk_now_msg(player_1, player_1_name, player_2, player_2_name):
    player_1 = int(player_1)
    player_2 = int(player_2)
    player_1_name = str(player_1_name)
    player_2_name = str(player_2_name)
    list_msg = []
    win = None
    bullet_list = random_bullet()
    for x in range(len(bullet_list)):
        if x % 2 == 0:
            if bullet_list[x] == 0:
                txt = random.choice(msg_pass[x])
                list_msg.append(
                    {"type": "node", "data": {"name": f"第{str(x + 1)}回合道友 {player_1_name}行动", "uin": player_1,
                                              "content": txt}})
            elif bullet_list[x] == 1:
                txt = random.choice(msg_died[x])
                list_msg.append(
                    {"type": "node", "data": {"name": f"第{str(x + 1)}回合道友 {player_1_name}行动", "uin": player_1,
                                              "content": txt}})
                win = 2
                break
            else:
                pass
        elif x % 2 == 1:
            if bullet_list[x] == 0:
                txt = random.choice(msg_pass[x])
                list_msg.append(
                    {"type": "node", "data": {"name": f"第{str(x + 1)}回合道友 {player_2_name}行动", "uin": player_2,
                                              "content": txt}})
            elif bullet_list[x] == 1:
                txt = random.choice(msg_died[x])
                list_msg.append(
                    {"type": "node", "data": {"name": f"第{str(x + 1)}回合道友 {player_2_name}行动", "uin": player_2,
                                              "content": txt}})
                win = 1
                break
            else:
                pass
        else:
            pass
    return list_msg, win


async def impart_pk_now_msg_to_bot(player_1_name, player_2_name):
    player_1_name = str(player_1_name)
    player_2_name = str(player_2_name)
    msg = ""
    win = None
    bullet_list = random_bullet()
    for x in range(len(bullet_list)):
        if x % 2 == 0:
            if bullet_list[x] == 0:
                msg += f"第{str(x + 1)}回合道友 {player_1_name}行动，出了一招！\n"

            elif bullet_list[x] == 1:
                msg += f"第{str(x + 1)}回合道友 {player_1_name}行动，出了一招，但失误了，败了！\n"
                win = 2
                break
            else:
                pass
        elif x % 2 == 1:
            if bullet_list[x] == 0:
                msg += f"第{str(x + 1)}回合 {player_2_name}行动，出了一招！\n"

            elif bullet_list[x] == 1:
                msg += f"第{str(x + 1)}回合 {player_2_name}行动，出了一招，但失误了，败了！\n"
                win = 1
                break
            else:
                pass
        else:
            pass
    return msg, win
