import { navbar } from "vuepress-theme-hope";

export default navbar([
  {
    text: "使用手册",
    icon: "creative",
    link: "/main/",
  },
  {
    text: "更新日志",
    icon: "creative",
    link: "/update/",
  },
  {
    text: "友链",
    icon: "creative",
    children: [
      {
        text: "Nonebot2",
        icon: "creative",
        link: "https://v2.nonebot.dev/",
      },
    ],
  },
]);
