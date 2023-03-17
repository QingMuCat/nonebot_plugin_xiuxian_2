try:
    import ujson as json
except ImportError:
    import json
from pathlib import Path
import os


class IMPART_PK(object):
    def __init__(self):
        self.dir_path = Path(__file__).parent
        self.data_path = os.path.join(self.dir_path, "impart_pk.json")
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except:
            self.info = {}
            data = json.dumps(self.info, ensure_ascii=False, indent=4)
            with open(self.data_path, mode="x", encoding="UTF-8") as f:
                f.write(data)
                f.close()
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

    def __save(self):
        """
        :return:保存
        """
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def check_user_impart(self, user_id):
        """
        核对用户是否存在
        :param user_id:
        """
        user_id = str(user_id)
        try:
            if self.data[user_id]:
                return True
        except:
            self.data[user_id] = {"pk_num": 3,
                                  "win_num": 0
                                  }
            self.__save()
            return False

    def find_user_data(self, user_id):
        """
        匹配用户数据
        :param user_id:
        """
        user_id = str(user_id)
        self.check_user_impart(user_id)
        try:
            data_ = self.data[user_id]
            return data_
        except:
            return None

    def update_user_data(self, user_id, type_):
        """
        匹配用户数据
        :param type_: TRUE or FALSE
        :param user_id:
        """
        user_id = str(user_id)
        self.check_user_impart(user_id)
        if type_:
            self.data[user_id]["win_num"] += 1
            self.__save()
            return True
        else:
            self.data[user_id]["pk_num"] -= 1
            self.__save()
            return True

    def all_user_data(self):
        """
        查找所有用户数据
        """
        try:
            dict_ = self.data
            return dict_
        except:
            return None

    def re_data(self):
        """
        重置数据
        """
        self.data = {}
        self.__save()


impart_pk = IMPART_PK()
