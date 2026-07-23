# 各平台一键登录 + 复用速查清单

> 配套技能：`qianjin-platform-analytics`
> 采集底座：`agent-browser`（Playwright 常驻会话，支持 `open/snapshot/screenshot/close` 与登录态保持）
> 采集脚本：`scripts/browser_capture.py`

本清单解决一个问题：**登录态真实爬取模式下，用户怎么登录、怎么复用**。

---

## 0. 前置须知（必读）

1. **登录步骤必须在你本机终端执行**，不能在 WorkBuddy 沙箱/远程环境执行——沙箱无显示器、也扫不了你的手机二维码。
2. 登录态按 `--session <名字>` 持久化到本地磁盘（Playwright storage state）。一次登录，后续脚本反复复用。
3. 各平台 session 有效时长几天到几周不等，过期后重新走一次"登录"即可。
4. **B站无需登录**即可拿公开数据（播放/点赞/投币/收藏），建议先拿它试跑整条流程。
5. 未登录也能用本技能——脚本会自动回退到 WebSearch 公开热榜 + 对标账号公开主页分析，只是拿不到精确播放/粉丝数。

---

## 1. 一键登录命令（各平台）

复制对应命令，在**本地终端**执行，弹出浏览器后用 App 扫码 / 输密码完成登录。

### 抖音（需登录）
```bash
agent-browser open "https://www.douyin.com" --headed --session dy --args "--no-sandbox"
```
> 登录后用抖音 App 扫网页二维码。session 名固定为 `dy`。`--args "--no-sandbox"` 是 Windows 兼容参数，可避免 `Chrome exited early` 报错。

### 快手（建议登录）
```bash
agent-browser open "https://www.kuaishou.com" --headed --session ks --args "--no-sandbox"
```
> 用快手 App 扫码。session 名 `ks`。

### 小红书（需登录）
```bash
agent-browser open "https://www.xiaohongshu.com" --headed --session xhs --args "--no-sandbox"
```
> 用小红书 App 扫二维码。session 名 `xhs`。

### 视频号（需登录微信）
```bash
agent-browser open "https://channels.weixin.qq.com" --headed --session sjh --args "--no-sandbox"
```
> 视频号在微信体系内，需登录微信网页版（扫码）。session 名 `sjh`。
> 注意：视频号网页数据较封闭，公开可抓字段有限，登录态主要用于访问创作者后台概览。

### 公众号（阅读/点赞数需登录 cookie）
```bash
agent-browser open "https://mp.weixin.qq.com" --headed --session wx --args "--no-sandbox"
```
> 用公众号管理员微信扫码登录 mp 后台。session 名 `wx`。
> 阅读/点赞/在看走私有接口 `getappmsgext`，需登录态 cookie（详见 wechat-analyzer 技能）。

### B站（可选登录，公开数据最友好）
```bash
agent-browser open "https://www.bilibili.com" --headed --session bili --args "--no-sandbox"
```
> 不登录也能抓。登录后仅用于解锁更高频请求额度 / 私信等，非必需。

---

## 2. 验证登录是否成功

登录后，在浏览器里打开该平台的「个人主页 / 创作中心」，确认能看到自己的头像、昵称或账号数据，即代表 session 已生效。

也可直接跑一次采集脚本（见第 3 节）验证：能拿到真实互动数（点赞/播放/粉丝）即登录成功；返回空或匿名数据则未登录。

---

## 3. 复用已登录 session 采集

登录完成后，用 `browser_capture.py` 带上同一个 `--session` 名即可复用，无需再次扫码。

### 通用格式
```bash
python scripts/browser_capture.py \
  --platform <douyin|kuaishou|xiaohongshu|shipinhao|weixin|bilibili> \
  --url "<目标视频/账号主页链接>" \
  --session <dy|ks|xhs|sjh|wx|bili> \
  --mode <snapshot|screenshot> \
  --out ./capture.json
```

### 示例：抓某抖音账号主页（已登录）
```bash
python scripts/browser_capture.py --platform douyin \
  --url "https://www.douyin.com/user/MS4wUAXXX" \
  --session dy --mode snapshot --out ./douyin_account.json
```

### 示例：抓某 B站视频（无需登录）
```bash
python scripts/browser_capture.py --platform bilibili \
  --url "https://www.bilibili.com/video/BV1xx411c7XD" \
  --mode snapshot --out ./bili_video.json
```

> 参数说明：
> - `--mode snapshot`：抓取页面 DOM + 关键字段（推荐，结构化）
> - `--mode screenshot`：仅截图（用于人工看图 / 视觉分析）
> - `--wait`：页面加载后额外等待秒数（默认 3），反爬慢的页面可加到 8
> - `--no-sandbox`：Linux/容器环境加此参数
> - `--timeout`：超时秒数（默认 30）

---

## 4. 批量一键登录脚本（可选）

把下面内容存为 `login_all.sh`，一次打开六个平台会话（需逐個扫码）：

```bash
#!/usr/bin/env bash
agent-browser open "https://www.douyin.com"            --headed --session dy  --args "--no-sandbox"
agent-browser open "https://www.kuaishou.com"          --headed --session ks  --args "--no-sandbox"
agent-browser open "https://www.xiaohongshu.com"       --headed --session xhs --args "--no-sandbox"
agent-browser open "https://channels.weixin.qq.com"    --headed --session sjh --args "--no-sandbox"
agent-browser open "https://mp.weixin.qq.com"          --headed --session wx  --args "--no-sandbox"
agent-browser open "https://www.bilibili.com"          --headed --session bili --args "--no-sandbox"
echo "六个平台会话已打开，请逐一扫码登录后关闭窗口。"
```

> Windows 用户可用 Git Bash 跑，或在 PowerShell 里逐条执行。

---

## 5. 会话失效 / 重新登录

当出现以下情况，重新执行第 1 节对应命令（同名 session 会覆盖旧状态）：
- 脚本返回空数据 / 跳转到登录页
- 平台提示"登录过期"
- 距离上次登录已超过约 2 周

重新登录用**同一个 `--session` 名**即可，后续采集命令不用改。

---

## 6. 速查表

| 平台 | 登录命令（本地执行，已带 Windows 兼容参数） | session 名 | 是否必需登录 | 公开数据友好度 |
|---|---|---|---|---|
| 抖音 | `agent-browser open "https://www.douyin.com" --headed --session dy --args "--no-sandbox"` | `dy` | ✅ 必需 | 低 |
| 快手 | `agent-browser open "https://www.kuaishou.com" --headed --session ks --args "--no-sandbox"` | `ks` | ⚠️ 建议 | 中 |
| 小红书 | `agent-browser open "https://www.xiaohongshu.com" --headed --session xhs --args "--no-sandbox"` | `xhs` | ✅ 必需 | 低 |
| 视频号 | `agent-browser open "https://channels.weixin.qq.com" --headed --session sjh --args "--no-sandbox"` | `sjh` | ✅ 必需 | 很低 |
| 公众号 | `agent-browser open "https://mp.weixin.qq.com" --headed --session wx --args "--no-sandbox"` | `wx` | ✅ 阅读数必需 | 低 |
| B站 | `agent-browser open "https://www.bilibili.com" --headed --session bili --args "--no-sandbox"` | `bili` | ❌ 不必需 | 高（推荐首选） |

---

## 7. 常见问题

**Q：能用无头模式（--no-headed）登录吗？**
A：不能。无头窗口无法显示二维码，扫不了。必须用 `--headed` 弹窗登录一次，之后脚本复用 session 时可以是无头。

**Q：登录态存在哪？**
A：agent-browser 按 session 名把 Playwright storage state 落在本地（通常在用户配置目录的 agent-browser 数据下）。WorkBuddy 不读取、不存储你的账号密码。

**Q：在沙箱里跑会怎样？**
A：沙箱无显示器 + 扫不了码，登录这步必然失败。请务必在本机终端执行第 1 节命令。

**Q：运行后报错 `Chrome exited early (exit code: 3) without writing DevToolsActivePort` 怎么办？**
A：这是 Windows 下 Chromium 沙箱启动失败的常见报错。在命令末尾加 `--args "--no-sandbox"` 即可：
```bash
agent-browser open "https://www.douyin.com" --headed --session dy --args "--no-sandbox"
```
如果仍失败，再加 `--disable-gpu --disable-dev-shm-usage`：
```bash
agent-browser open "https://www.douyin.com" --headed --session dy --args "--no-sandbox --disable-gpu --disable-dev-shm-usage"
```
零代码用户参见 `references/usage-tutorial.md` 的"登录时遇到报错怎么办"。

**Q：不登录能出赛道分析吗？**
A：能。脚本检测到无 session / 匿名数据时，自动回退 WebSearch 公开热榜 + 对标账号公开主页分析，照样产出赛道概览、对标拆解、热点选题与运营建议，只是互动数据为估算/公开口径。
