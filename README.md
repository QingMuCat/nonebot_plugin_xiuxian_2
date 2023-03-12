# 修仙2.0

## 简介

本插件主要为实现群聊修仙功能,最近经常封号，请自行判断后再使用，已默认转成图片模式，如需关闭，可在config.py处调整img字段为false

## 设定征集中，有好的想法可以推送给我哦~~~

## 更新2023.3.1
1.修复已知bug
2.支持每个群boss刷新时间定制
3.支持适配修仙1的境界
3.宗门可以根据道号踢人
4.支持随机存档背景
5.支持批量使用丹药
6.支持批量炼金和炼金绑定丹药
7.修改了世界积分价格,需要删除boss模块下的config.json生效
8.增加了修仙全局命令调用锁,默认一分钟五次
9.增加隐藏职业：器师
器师：指依托于大宗门下的炼器士，其修为一般很低，但不可小觑，因为一般是大修士的转生与亲信，替大修士完成红尘历练。
## 更新2023.3.11
1.修改背包容量
2.坊市支持批量上架和购买
3.解决手机部分图片需要点开才能看到字的问题

## 安装
1、下载插件文件
- 使用nb(推荐虚拟环境安装)
```
nb plugin install nonebot_plugin_xiuxian_2
```
- 使用pip(推荐虚拟环境安装)
```
pip install nonebot_plugin_xiuxian_2
```

- 使用github处拉取源码使用
无镜像：

```
git clone https://github.com/QingMuCat/nonebot_plugin_xiuxian_2.0
```

镜像：https://ghproxy.com/
```
git clone https://ghproxy.com/https://github.com/QingMuCat/nonebot_plugin_xiuxian_2.0
```
- 使用gitee处拉取源码使用（同步更新）
```
git clone https://gitee.com/july-meow/nonebot_plugin_xiuxian_2.0
```
2、如果遇到问题，请先百度和查看下方的 【一些问题】

3、如解决不了进交流群：760517008 提问，提问请贴上完整的日志

## 配置文件
1、配置文件一般在data/xiuxian文件夹下，自行按照json格式修改即可，一些字段的含义可以进群交流<br>
2、子插件的配置会在插件运行后在子插件文件中生成config.json文件，该文件字段含义在同级目录的xxxconfig.py有备注。注意：修改配置只需要修改json即可，修改.py文件的话需要删除json文件才会生效，任何修改都需要重启bot<br>
3.卡图下载地址：[卡图](https://cowtransfer.com/s/82b90d2b879d43):口令：k3jzr5，文件放置于data/xiuxian目录下<br>

## 风控配置
配置地址:修仙插件下xiuxian_config.py
在只有一个qq链接的情况下风控配置应该全部为空，即不配置
self.put_bot = []  # 接收消息qq,主qq,框架将只处理此qq的消息，不配置将默认设置第一个链接的qq为主qq
self.main_bo = []  # 负责发送消息的qq,调用lay_out.py 下range_bot函数的情况下需要填写
self.shield_group = []  # 屏蔽的群聊
self.layout_bot_dict = {{}}  # QQ所负责的群聊{{群 :bot}}   其中 bot类型 []或str 
示例： {
    "群123群号" : "对应发送消息的qq号"
    "群456群号" ： ["对应发送消息的qq号1","对应发送消息的qq号2"]
}
当后面qq号为一个字符串时为一对一，为列表时为多对一

## 一些问题
- 当为放置为plugins目录使用时，请修改根目录下__init__.py文件中的42行：src=''中的内容，填写的是存放插件的目录，一般情况下 src='src.plugins.'  如有不同请按照格式修改
## 特别感谢

- [NoneBot2](https://github.com/nonebot/nonebot2)：本插件实装的开发框架，NB天下第一可爱。
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)：稳定完善的 CQHTTP 实现。
- [nonebot_plugin_xiuxian](https://github.com/s52047qwas/nonebot_plugin_xiuxian)：原版修仙

## 插件依赖

- nonebot2
- nonebot-adapter-onebot
- go-cqhttp

## 支持

大家喜欢的话可以给这个项目点个star

有bug、意见和建议都欢迎提交 [Issues](https://github.com/QingMuCat/nonebot_plugin_xiuxian_2.0/issues) 
或者联系进入QQ交流群：760517008

## 许可证
本项目使用 [MIT](https://choosealicense.com/licenses/mit/) 作为开源许可证
