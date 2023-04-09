---
title: 安装
order: 2
---

## 下载

* 使用 pip
```cmd
pip install nonebot_plugin_xiuxian_2
```
* 使用 nb-cli
```cmd
nb plugin install nonebot_plugin_xiuxian_2
```
* 使用 git
```cmd
git clone https://github.com/QingMuCat/nonebot_plugin_xiuxian_2.git
```
使用镜像：`git clone https://ghproxy.com/https://github.com/QingMuCat/nonebot_plugin_xiuxian_2`

## 配置

### 资源文件
1. 配置文件一般在 `data/xiuxian` 文件夹下，初次启动修仙插件时会自动生成一部分。修改配置只需修改json文件即可，**任何修改都需要重启bot**
2. 除此之外，您还需要[下载卡图](https://cowtransfer.com/s/82b90d2b879d43)，将解压后的卡图放置于 `data/xiuxian` 目录下

### 分控配置（可选）
若您有多个QQ机器人链接的需求，可以在 `xiuxian_config.py` 配置
```py
self.put_bot = [] 
self.main_bo = []
self.shield_group = []
self.layout_bot_dict = {{}}
```
参数：  
* `self.put_bot`：
    - 默认为空
    - 接收消息QQ，主QQ，插件将只处理此QQ的消息，不配置将默认设置第一个链接的QQ为主QQ
* `self.main_bo`：
    - 默认为空
    - 负责发送消息的QQ，调用 `lay_out.py` 下 range_bot函数 的情况下需要填写
* `self.shield_group`：
    - 默认为空
    - 参数：群号
    - 屏蔽的群聊
* `self.layout_bot_dict`：
    - 默认为空
    - 参数：{群 :bot}。其中 bot 类型为列表或字符串
    - QQ所负责的群聊    
    - 例子：
    ```py
        self.layout_bot_dict = {{
            "111": "xxx",               # 由QQ号为xxx的机器人单独负责111群聊
            "222": ["yyy", "zzz"]       # 由QQ号为yyy和zzz的机器人同时负责222群聊
        }}
    ```

### 文件夹配置（可选）
~~以下皆为适合强迫症者看的废话~~

如果您是将 修仙插件 下载到本地的，相信肯定不会以 `nonebot_plugin_xiuxian_2` 命名插件，这时为了避免报错，您需要将高光部分修改为自己重命名后的名字
```python{1,5}
if get_plugin_by_module_name("nonebot_plugin_xiuxian_2"):
    logger.info("推荐直接加载 nonebot_plugin_xiuxian_2 仓库文件夹")
    load_all_plugins(
        [
            f"nonebot_plugin_xiuxian_2.{module.name}"
            for module in iter_modules([str(Path(__file__).parent)])
            if module.ispkg
            and (
                (name := module.name[11:]) == "meta"
                or name not in _config.disabled_plugins
            )
            # module.name[:11] == xiuxian_
        ],
        [],
    )
```
::: details 再详细点？
如果，你是用 `git` 将修仙下载至本地，我们的目录结构是这样的：
```
📂 plugins
└── 📂 nonebot_plugin_xiuxian_2
    └── 📜 __init__.py
    └── ...
```
~~为了好看~~ ，但是我们通常会将原名修改为自己喜欢的名字，这时目录结构就变成了这样：
```
📂 plugins
└── 📂 xiuxian
    └── 📜 __init__.py
    └── ...
```
为了避免报错，您需要将上面代码的高光部分修改为自己重命名后的名字，即：
```py
if get_plugin_by_module_name("xiuxian"):
    logger.info("推荐直接加载 nonebot_plugin_xiuxian_2 仓库文件夹")
    load_all_plugins(
        [
            f"xiuxian.{module.name}"
            for module in iter_modules([str(Path(__file__).parent)])
            if module.ispkg
            and (
                (name := module.name[11:]) == "meta"
                or name not in _config.disabled_plugins
            )
            # module.name[:11] == xiuxian_
        ],
        [],
    )
```
:::