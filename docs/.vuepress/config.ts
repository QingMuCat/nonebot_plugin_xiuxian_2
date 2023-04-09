import { defineUserConfig } from "vuepress";
import theme from "./theme";
import { searchProPlugin } from "vuepress-plugin-search-pro";
export default defineUserConfig({

  title: "nonebot-plugin-xiuxian-2",
  description: "基于Nonebot的 修仙插件 使用说明书",
  theme,
  shouldPrefetch: false,
  plugins: [
    searchProPlugin({
      locales: {
        "/": {
          placeholder: "搜索",
        },
        "/en/": {
          placeholder: "Search",
        },
      },
      indexContent: true,
    }),
  ],
});
