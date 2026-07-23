# 六平台数据采集指南

> 配合 `scripts/browser_capture.py`（模式 A）与 `WebSearch` / `WebFetch`（模式 B）。
> 标注各平台登录需求、公开数据获取入口、采集注意点。

## 通用前置
- 模式 A 登录：`agent-browser open <平台URL> --headed --session <key>`，扫码后保持会话。
  - session key 建议：抖音 `dy` / 快手 `ks` / 小红书 `xhs` / B站 `bili` / 公众号 `wxg` / 视频号 `sph`
- 采集：`python scripts/browser_capture.py --platform <key> --url <URL> --session <key> --mode snapshot|screenshot --out ./capture`

---

## 1. 抖音 douyin
- 主页：https://www.douyin.com
- 登录需求：✅ 必须（看播放 / 点赞需登录；未登录仅见部分推荐流）
- 公开入口：抖音热点榜（https://www.douyin.com/hot）、巨量算数（https://trendinsight.oceanengine.com）
- 采集注意：PC 网页版结构常变；推荐用「用户主页 URL」做对标账号采集
- 对标账号 URL：https://www.douyin.com/user/<sec_uid>

## 2. 快手 kuaishou
- 主页：https://www.kuaishou.com
- 登录需求：✅ 必须
- 公开入口：快手热榜、快手指数
- 对标账号 URL：https://www.kuaishou.com/profile/<userId>

## 3. 微信公众号 gzh
- 入口：搜狗微信（https://weixin.sogou.com）搜公众号 / 文章（无需登录可见列表）
- 登录需求：⚠️ 看单篇阅读 / 点赞需微信登录（用 `qianjin-wechat-analyzer` 的 `fetch_metrics.py` 或浏览器登录）
- 采集注意：公众号数据受私有接口限制，详见 `qianjin-wechat-analyzer` §2.4 / §2.5
- 对标：搜狗微信搜赛道关键词，取高阅读账号

## 4. 小红书 xhs
- 主页：https://www.xiaohongshu.com
- 登录需求：✅ 必须（发现页 / 笔记数据需登录）
- 公开入口：小红书网页版搜索（登录后）、蒲公英平台（官方商业化数据）
- 对标账号 URL：https://www.xiaohongshu.com/user/profile/<userId>

## 5. B站 bilibili
- 主页：https://www.bilibili.com
- 登录需求：❌ 无需（播放 / 点赞 / 投币 / 收藏公开可见，最友好）
- 公开入口：B站热门（https://www.bilibili.com/v/popular/all）、分区排行、搜索
- 对标账号 URL：https://space.bilibili.com/<uid>
- 采集：模式 B（WebFetch 直接读公开页）即可，无需登录

## 6. 视频号 sph
- 入口：微信内（无独立 PC 网页版），难用 agent-browser 直接抓
- 登录需求：✅ 必须且受限（需微信客户端）
- 替代方案：用「视频号热门」榜单页、第三方数据平台（新视 / 友望）公开侧做模式 B 采集
- 注意：视频号数据透明度最低，报告中标注可信度为低

---

## 反爬与风控
- 采集频率克制，避免短时间大量请求
- 登录态会话定期重登（cookie 过期）
- 截图 / 视觉读取优于暴力解析 DOM（更稳定）
