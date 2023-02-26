try:
    import ujson as json
except ImportError:
    import json
import os
from pathlib import Path

configkey = ["open", "auctions", "交友会定时参数"]
CONFIG = {
    "open": [],
    "auctions": {
        "渡厄丹": {
            "id": 1999,
            "start_price": 100000,
        },
        "鬼面炼心丹": {
            "id": 1503,
            "start_price": 150000,
        },
        "筑基丹": {
            "id": 1400,
            "start_price": 50000,
        },
        "聚顶丹": {
            "id": 1401,
            "start_price": 60000,
        },
        "朝元丹": {
            "id": 1402,
            "start_price": 60000,
        },
        "锻脉丹": {
            "id": 1403,
            "start_price": 90000,
        },
        "护脉丹": {
            "id": 1404,
            "start_price": 90000,
        },
        "天命淬体丹": {
            "id": 1405,
            "start_price": 150000,
        },
        "澄心塑魂丹": {
            "id": 1406,
            "start_price": 150000,
        },
        "混元仙体丹": {
            "id": 1407,
            "start_price": 150000,
        },
        "黑炎丹": {
            "id": 1408,
            "start_price": 300000,
        },
        "金血丸": {
            "id": 1409,
            "start_price": 300000,
        },
        "虚灵丹": {
            "id": 1410,
            "start_price": 450000,
        },
        "净明丹": {
            "id": 1411,
            "start_price": 450000,
        },
        "安神灵液": {
            "id": 1412,
            "start_price": 550000,
        },
        "魇龙之血": {
            "id": 1413,
            "start_price": 550000,
        },
        "化劫丹": {
            "id": 1414,
            "start_price": 700000,
        },
        "太上玄门丹": {
            "id": 1415,
            "start_price": 1500000,
        },
        "金仙破厄丹": {
            "id": 1416,
            "start_price": 2000000,
        },
        "太乙炼髓丹": {
            "id": 1417,
            "start_price": 2500000,
        },
        "地仙玄丸": {
            "id": 2014,
            "start_price": 500000,
        },
        "消冰宝丸": {
            "id": 2015,
            "start_price": 1000000,
        },
        "元磁神光": {
            "id": 9910,
            "start_price": 5500000,
        },
        "天罗真功": {
            "id": 9911,
            "start_price": 5500000,
        },
        "托天魔功": {
            "id": 9912,
            "start_price": 5500000,
        },
        "大罗仙印": {
            "id": 8911,
            "start_price": 5500000,
        },
        "生骨丹": {
            "id": 1101,
            "start_price": 1000,
        },
        "化瘀丹": {
            "id": 1102,
            "start_price": 3000,
        },
        "培元丹": {
            "id": 1103,
            "start_price": 5000,
        },
        "培元丹plus": {
            "id": 1104,
            "start_price": 10000,
        },
        "黄龙丹": {
            "id": 1105,
            "start_price": 15000,
        },
        "回元丹": {
            "id": 1106,
            "start_price": 25000,
        },
        "回春丹": {
            "id": 1107,
            "start_price": 40000,
        },
        "养元丹": {
            "id": 1108,
            "start_price": 60000,
        },
        "太元真丹": {
            "id": 1109,
            "start_price": 80000,
        },
        "九阳真丹": {
            "id": 1110,
            "start_price": 10000,
        },
    },
    "交友会定时参数": {  # 交友会生成的时间，每天的17-23点
        "hours": "17-23"
    }
}


def get_config():
    try:
        config = readf()
        for key in configkey:
            if key not in list(config.keys()):
                config[key] = CONFIG[key]
        savef(config)
    except:
        config = CONFIG
        savef(config)
    return config


CONFIGJSONPATH = Path(__file__).parent
FILEPATH = CONFIGJSONPATH / 'config.json'


def readf():
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)


def savef(data):
    data = json.dumps(data, ensure_ascii=False, indent=3)
    savemode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=savemode, encoding="UTF-8") as f:
        f.write(data)
        f.close()
    return True
