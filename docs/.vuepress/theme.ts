import { hopeTheme } from "vuepress-theme-hope";
import navbar from "./navbar";

export default hopeTheme({
  hostname: "https://xiuxian.netlify.app",
  author: {
    name: "mute.",
    url: "https://github.com/mute23-code",
  },

  //pure:true,
  themeColor: {
    blue: "#2196f3",
    red: "#f26d6d",
    green: "#3eaf7c",
    orange: "#fb9b5f",
  },
  backToTop: true,
  iconAssets: "iconfont",
  logo: "",
  repo: "QingMuCat/nonebot_plugin_xiuxian_2",
  lastUpdated: true,
  locales: {
    "/": {
      navbar: navbar,
    },
    "/en/": {
      navbar: [
        {
          text: "Docs",
          icon: "creative",
          link: "/main/",
        },
        {
          text: "Update",
          icon: "creative",
          link: "/update/",
        },
        {
          text: "Links",
          icon: "creative",
          children: [
            {
              text: "Nonebot2",
              icon: "creative",
              link: "https://v2.nonebot.dev/",
            }
          ],
        },
      ],
    }
  },
  sidebar: {
    "/main/": "structure",
    "/update/": "structure",
  },
  footer: "后面没有了哦~",
  displayFooter: true,
  copyright:
    "MIT Licensed / CC-BY-NC-SA | Copyright © 2022-present QingMuCat & mute.",
  pageInfo: ["Author", "ReadingTime", "Word"],
  encrypt: {
    config: {
      "/guide/encrypt.html": ["1234"],
    },
  },
  plugins: {
    git: {
      updatedTime: true,
      contributors: true,
      createdTime: false,
    },
    photoSwipe: {},
    pwa: {
      showInstall: true,
    },
    sitemap: {},
    mdEnhance: {
      gfm: true,
      container: true,
      tabs: true,
      codetabs: true,
      align: true,
      tasklist: true,
      flowchart: true,
      stylize: [],
      presentation: false,
    },
  },
});
