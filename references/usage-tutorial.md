# 完整新手使用教程（零代码版）

> 配套技能：`qianjin-platform-analytics`
> 适用对象：不会写代码、第一次用命令行的用户

本教程不讲原理，只讲**每一步按什么、点哪里、贴什么**。跟着做就行。

---

## 一、你需要准备什么

1. **一台 Windows 电脑**（Mac 大同小异，命令相同）
2. **WorkBuddy 已安装**，并且技能 `qianjin-platform-analytics` 已加载
3. **一个本地终端窗口**（后面会教你怎么打开）
4. **各平台的手机 App**（抖音、快手、小红书、微信等，用来扫码登录）

> 不需要会写代码，也不需要懂技术名词，只需要会复制、粘贴、扫码。

---

## 二、怎么打开命令窗口（CMD）

你截图里的黑窗口就是命令窗口。打开方式有三种，任选一种：

### 方法 A：快捷键最快（推荐）
1. 同时按键盘上的 `Win + R`
2. 弹出的"运行"窗口里输入：`cmd`
3. 按回车，就会出现黑色的命令窗口

### 方法 B：开始菜单
1. 点屏幕左下角的"开始"按钮
2. 搜索 `cmd` 或 `命令提示符`
3. 点击打开

### 方法 C：在 WorkBuddy 里
如果你当前就在 WorkBuddy 的终端/命令工具里，也可以直接粘贴命令。

打开后你会看到类似这样的提示：
```
C:\Users\ZQJ>
```
后面的 `>` 表示它在等你输入命令。

---

## 三、第一次登录抖音（完整示范）

### 第 1 步：复制登录命令

把下面这一整行复制：
```bash
agent-browser open "https://www.douyin.com" --headed --session dy --args "--no-sandbox"
```

### 第 2 步：粘贴到 CMD 里，按回车

在 CMD 窗口里点一下鼠标右键，命令就会贴进去，然后按回车。

> 注意：在 CMD 里粘贴不是 `Ctrl+V`，而是**右键 → 粘贴**。

### 第 3 步：扫码登录

回车后，会弹出一个 Chrome/Chromium 浏览器窗口，打开抖音网页。
- 如果看到二维码，拿出手机抖音 App 扫一扫
- 如果让你输手机号验证码，按提示操作

登录成功后，能看到你的抖音头像和昵称，就说明好了。

### 第 4 步：关闭浏览器窗口

登录成功后，可以把弹出的浏览器窗口关掉。登录态已经按名字 `dy` 保存到电脑里了。

---

## 四、登录时遇到报错怎么办

### 常见报错：`Chrome exited early (exit code: 3)`

如果你运行后看到下面这样的红字：
```
X Chrome exited early (exit code: 3) without writing DevToolsActivePort
Hint: try passing --args "--no-sandbox" if Chrome crashes silently...
```

这不是你的错，是 Windows 环境下 Chromium 沙箱启动失败。解决方式很简单：

**在刚刚那条命令末尾加上 `--args "--no-sandbox"`。**

示例：
```bash
agent-browser open "https://www.douyin.com" --headed --session dy --args "--no-sandbox"
```

加完再跑一次，浏览器窗口就能正常弹出来了。

### 如果加了还是弹不出

尝试再加两个兼容参数：
```bash
agent-browser open "https://www.douyin.com" --headed --session dy --args "--no-sandbox --disable-gpu --disable-dev-shm-usage"
```

---

## 五、怎么采集数据（以抖音为例）

登录完成后，就可以跑采集脚本了。假设你想分析抖音的"美妆护肤"赛道，可以先抓一个对标账号主页试试。

### 第 1 步：确认你在技能目录里

在 CMD 里输入：
```bash
cd "C:\Users\ZQJ\.workbuddy\skills\qianjin-platform-analytics\scripts"
```
然后按回车。

> 上面的路径是技能存放位置，如果你装在不同位置，把路径改成你的。

### 第 2 步：复制采集命令

示例：抓一个抖音账号主页
```bash
python browser_capture.py --platform douyin --url "https://www.douyin.com/user/这里换成账号ID" --session dy --mode snapshot --out ./my_first_capture.json
```

注意把 `https://www.douyin.com/user/这里换成账号ID` 换成你要抓的真实链接。

### 第 3 步：看结果

脚本跑完后，会在 `scripts` 文件夹里生成一个 `my_first_capture.json` 文件。里面会有类似这样的内容：
```json
{
  "url": "https://www.douyin.com/user/xxx",
  "title": "xxx的主页",
  "description": "...",
  "author": "xxx",
  "follower_count": "12.5万",
  "like_count": "386.2万",
  "status": "ok"
}
```

具体能抓到哪些字段，取决于平台是否公开、是否已登录。B站公开数据最全，建议先用 B站 试跑。

---

## 六、怎么让 AI 帮你分析

采集脚本只能拿到原始数据，真正的赛道分析（行业趋势、对标账号、热点选题、运营建议）是 WorkBuddy 里的 `qianjin-platform-analytics` 技能来做的。

你可以直接对 WorkBuddy 说：
```
分析抖音 美妆护肤赛道（登录态）
```

WorkBuddy 会自动：
1. 调用 `browser_capture.py` 采集公开/登录数据
2. 结合 WebSearch 搜索公开热榜
3. 生成一份赛道分析报告

如果你已经登录过，就加一句"登录态"；没登录也能跑，只是深度数据会少一些。

---

## 七、各平台登录命令一览（复制即用）

| 平台 | 复制这条命令 |
|---|---|
| 抖音 | `agent-browser open "https://www.douyin.com" --headed --session dy --args "--no-sandbox"` |
| 快手 | `agent-browser open "https://www.kuaishou.com" --headed --session ks --args "--no-sandbox"` |
| 小红书 | `agent-browser open "https://www.xiaohongshu.com" --headed --session xhs --args "--no-sandbox"` |
| 视频号 | `agent-browser open "https://channels.weixin.qq.com" --headed --session sjh --args "--no-sandbox"` |
| 公众号 | `agent-browser open "https://mp.weixin.qq.com" --headed --session wx --args "--no-sandbox"` |
| B站 | `agent-browser open "https://www.bilibili.com" --headed --session bili --args "--no-sandbox"` |

> `--args "--no-sandbox"` 是 Windows 兼容参数，加了更稳。

---

## 八、常见问题

**Q：CMD 里粘贴命令后没反应？**
A：按一下回车。如果还没反应，检查是不是命令太长被截断，建议分步复制。

**Q：浏览器弹出来后没有二维码？**
A：先等 5 秒让页面加载完。如果还是没有，点网页右上角或"登录"按钮，通常就能调出二维码。

**Q：扫码后提示登录成功，但脚本抓不到数据？**
A：可能是 session 过期了，重新执行一次登录命令同名覆盖即可。

**Q：我不想登录，能不能直接分析？**
A：能。直接对 WorkBuddy 说"分析 B站 动漫赛道"，不登录也能出基础报告。B站公开数据最友好，建议先试它。

**Q：为什么要在 CMD 里操作？不能像普通软件一样点按钮吗？**
A：`agent-browser` 目前没有图形按钮版，需要用命令启动。但本质上就是"复制 → 粘贴 → 回车"，三步搞定。

---

## 九、完整流程图

```
打开 CMD
  ↓
粘贴 agent-browser open 命令 → 回车
  ↓
弹出浏览器 → 扫码登录
  ↓
关闭浏览器
  ↓
对 WorkBuddy 说：分析 XX 平台 XX 赛道
  ↓
等 AI 生成赛道分析报告
```

---

**遇到问题把报错截图发给我，我帮你排。**
