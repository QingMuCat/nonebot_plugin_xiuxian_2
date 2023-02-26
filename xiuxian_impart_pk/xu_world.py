try:
    import ujson as json
except ImportError:
    import json
from pathlib import Path
import os


class XU_WORLD(object):
    def __init__(self):
        self.dir_path = Path(__file__).parent
        self.data_path = os.path.join(self.dir_path, "x_world.json")
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

    def check_xu_world_num(self):
        """
        查看人数
        """
        num = len(self.data.keys())
        if num > 40:
            return False
        else:
            return True

    def check_xu_world_user_id(self, user_id):
        """
        检查是否加入
        """
        user_id = str(user_id)
        try:
            if self.data[user_id]:
                return True
        except:
            return False

    def add_xu_world(self, user_id):
        """
        加入虚神界
        """
        user_id = str(user_id)
        if self.check_xu_world_user_id(user_id):
            return "你已经在虚神界中了！"

        if self.check_xu_world_num:
            self.data[user_id] = True
            self.__save()
            return "加入虚神界成功！"
        else:
            return "虚神界人数已满，道友现在无法加入！"

    def del_xu_world(self, user_id):
        """
        加入虚神界
        """
        user_id = str(user_id)
        del self.data[user_id]
        self.__save()

    def all_xu_world_user(self):
        """
        全部虚神界用户
        """
        all_user = self.data.keys()
        if all_user is None:
            return None
        else:
            return list(all_user)

    def re_data(self):
        """
        重置数据
        """
        self.data = {}
        self.__save()


xu_world = XU_WORLD()
