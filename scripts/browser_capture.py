#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
browser_capture.py —— 多平台赛道数据采集（基于 agent-browser）

等价 OpenClaw 的 browser 常驻服务：保持登录态会话，open / snapshot / screenshot / close。
是 qianjin-platform-analytics 技能「模式 A（登录态真实爬取）」的可执行入口。

依赖（本机一次性安装）:
    npm install -g agent-browser
    agent-browser install        # 下载 Chromium

典型用法:
  1) 先登录平台（保留会话，不关闭）:
       agent-browser open https://www.douyin.com --headed --session dy
       # 在弹出的浏览器里扫码/登录，登录成功后保持窗口或只保持 daemon
  2) 采集对标账号主页（DOM 文本，供脚本粗提取互动数）:
       python scripts/browser_capture.py --platform douyin --url <主页URL> --session dy --mode snapshot --out ./capture
  3) 或截图（交给带视觉的 agent 读数字，更准）:
       python scripts/browser_capture.py --platform xhs --url <笔记页> --session xhs --mode screenshot --out ./capture
  4) 用完关掉会话:
       agent-browser close --session dy

输出:
    --out 目录下生成：
      - <标识>.txt   （mode=snapshot 时的 DOM 文本）
      - <标识>.png   （mode=screenshot 时的整页截图）
    控制台打印 JSON: {"platform":..., "session":..., "results":[...], "failed":[...]}

注意:
    - 抖音/快手/小红书/视频号必须登录才能看到完整互动数据；B站 公开可见（无需登录）。
    - 各平台 DOM 结构常变，snapshot 模式的「粗提取」为参考实现，可能漏抓；
      关键数字建议用 mode=screenshot 交给视觉 agent 读，更准确。
    - Windows 上 agent-browser 是 .cmd 包装，Python subprocess 无法直接调用，
      故改用 node 直接跑其 JS 入口（复用 qianjin-wechat-analyzer/browse_metrics.py 的写法）。
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

# ---------------------------------------------------------------------------
# agent-browser 解析（复用自 qianjin-wechat-analyzer/scripts/browse_metrics.py）
# ---------------------------------------------------------------------------

def _pkg_js(pkg_dir):
    """从包目录读 package.json 的 bin 入口，返回存在的 JS 绝对路径或 None。"""
    pkg_json = os.path.join(pkg_dir, "package.json")
    if not os.path.isfile(pkg_json):
        return None
    try:
        with open(pkg_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        binrel = (data.get("bin") or {}).get("agent-browser")
        if not binrel:
            return None
        js = os.path.join(pkg_dir, binrel.lstrip("./\\"))
        return js if os.path.isfile(js) else None
    except Exception:  # noqa
        return None


def resolve_agent_browser():
    """返回 agent-browser 的调用方式（命令 base 列表），找不到返回 None。

    Windows 上 agent-browser 是 .cmd 包装脚本，Python subprocess 无法直接调用，
    因此改用 node 直接跑其 JS 入口（node 才是真正的 exe，参数走 argv 更安全）。
    不依赖 `npm` 命令（它在 Python 的 PATH 里常常缺失）。
    """
    node = shutil.which("node")
    ab = shutil.which("agent-browser")
    if ab:
        npm_prefix = os.path.dirname(ab)
        pkg_dir = os.path.join(npm_prefix, "node_modules", "agent-browser")
        js = _pkg_js(pkg_dir)
        if node and js:
            return [node, js]
    for pkg_dir in (
        os.path.expanduser("~/AppData/Roaming/npm/node_modules/agent-browser"),
        os.path.expanduser("~/npm/node_modules/agent-browser"),
        "/usr/local/lib/node_modules/agent-browser",
        "/usr/lib/node_modules/agent-browser",
    ):
        js = _pkg_js(pkg_dir)
        if node and js:
            return [node, js]
    if ab:
        return ["agent-browser"]
    return None


def run(cmd, timeout=60):
    """执行命令，返回 (rc, stdout, stderr)。失败不抛异常。"""
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="ignore",
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:  # noqa
        return 1, "", str(e)


def safe_name(url):
    """从 URL 提取可辨识文件名。"""
    m = re.search(r"sec_uid=([^&]+)", url)
    if m:
        return "u_" + re.sub(r"[^A-Za-z0-9]", "", m.group(1))[:16]
    m = re.search(r"userId=([^&]+)", url)
    if m:
        return "u_" + m.group(1)
    m = re.search(r"uid[=/](\d+)", url)
    if m:
        return "u_" + m.group(1)
    m = re.search(r"profile/([A-Za-z0-9_-]+)", url)
    if m:
        return "u_" + m.group(1)
    m = re.search(r"/s/([A-Za-z0-9_-]+)", url)
    if m:
        return "s_" + m.group(1)
    return "art_" + str(abs(hash(url)) % 10**8)


# ---------------------------------------------------------------------------
# 启发式提取（参考实现，DOM 常变时可能漏抓）
# ---------------------------------------------------------------------------

INTERACTION_PATTERNS = [
    (r"点赞[：:\s]*([\d.]+[wW万]?)", "likes"),
    (r"播放[：:\s]*([\d.]+[wW万]?)", "plays"),
    (r"评论[：:\s]*([\d.]+[wW万]?)", "comments"),
    (r"收藏[：:\s]*([\d.]+[wW万]?)", "favorites"),
    (r"转发[：:\s]*([\d.]+[wW万]?)", "shares"),
    (r"(\d+(?:\.\d+)?[wW万]?)\s*赞", "likes"),
    (r"(\d+(?:\.\d+)?[wW万]?)\s*播放", "plays"),
    (r"(\d+(?:\.\d+)?[wW万]?)\s*评论", "comments"),
]


def extract_from_snapshot(text):
    """从 snapshot DOM 文本里粗提取互动数字。参考实现，漏抓请改用 screenshot 模式。"""
    data = {}
    for pat, key in INTERACTION_PATTERNS:
        m = re.search(pat, text)
        if m and key not in data:
            data[key] = m.group(1)
    return data


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="用 agent-browser 采集多平台赛道数据")
    ap.add_argument("--platform", required=True,
                    choices=["douyin", "kuaishou", "gzh", "xhs", "bili", "sph"],
                    help="目标平台（决定输出归属与提示）")
    ap.add_argument("--url", help="单个页面链接")
    ap.add_argument("--urls", help="包含多个链接的文件，每行一个")
    ap.add_argument("--out", default="./capture", help="输出目录（默认 ./capture）")
    ap.add_argument("--session", default=None, help="复用指定的 agent-browser 会话（共享登录态）")
    ap.add_argument("--mode", default="snapshot", choices=["snapshot", "screenshot"],
                    help="snapshot=导出 DOM 文本并粗提取；screenshot=整页截图供视觉读取")
    ap.add_argument("--headed", action="store_true", help="显示浏览器窗口（首次登录时用）")
    ap.add_argument("--no-close", action="store_true", help="结束后不关闭浏览器 daemon（便于复用登录态）")
    ap.add_argument("--wait", default="networkidle", choices=["networkidle", "load", "domcontentloaded"],
                    help="打开页面后的等待策略（卡住时降级为 load）")
    ap.add_argument("--timeout", type=int, default=90, help="单条命令超时秒数")
    ap.add_argument("--args", action="append", default=[],
                    help="透传给浏览器的启动参数，例如 --args=--no-sandbox")
    ap.add_argument("--no-sandbox", action="store_true",
                    help="以 --no-sandbox 启动浏览器（沙箱/容器环境常需）")
    args = ap.parse_args()

    if not args.url and not args.urls:
        ap.error("必须提供 --url 或 --urls 之一")

    base = resolve_agent_browser()
    if not base:
        sys.stderr.write(
            "未找到 agent-browser。请先安装：\n"
            "  npm install -g agent-browser\n"
            "  agent-browser install\n"
        )
        return 2

    urls = []
    if args.url:
        urls.append(args.url.strip())
    if args.urls:
        with open(args.urls, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
    if not urls:
        sys.stderr.write("没有可处理的链接。\n")
        return 1

    os.makedirs(args.out, exist_ok=True)
    common = ["--session", args.session] if args.session else []

    results, failed = [], []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] 采集: {url}", file=sys.stderr)
        # 1) 打开
        open_cmd = base + ["open", url] + common
        if args.headed:
            open_cmd.append("--headed")
        if args.no_sandbox:
            open_cmd += ["--args", "--no-sandbox"]
        open_cmd += args.args
        rc, out, err = run(open_cmd, timeout=args.timeout)
        if rc != 0:
            failed.append({"url": url, "error": f"open failed: {err.strip() or out.strip()}"})
            continue
        # 2) 等待渲染（可降级）
        rc, out, err = run(base + ["wait", "--load", args.wait] + common, timeout=args.timeout)
        if rc != 0 and args.wait != "load":
            run(base + ["wait", "--load", "load"] + common, timeout=args.timeout)

        rec = {"url": url, "platform": args.platform}
        if args.mode == "snapshot":
            # 3a) 导出 DOM 文本
            rc, snap, err = run(base + ["snapshot"] + common, timeout=args.timeout)
            if rc != 0:
                failed.append({"url": url, "error": f"snapshot failed: {err.strip() or snap.strip()}"})
                continue
            txt_path = os.path.join(args.out, f"{safe_name(url)}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(snap)
            rec["snapshot_file"] = txt_path
            rec["extracted"] = extract_from_snapshot(snap)
            print(f"    已保存 DOM: {txt_path} | 粗提取: {rec['extracted']}", file=sys.stderr)
        else:
            # 3b) 整页截图（交视觉 agent 读）
            png_path = os.path.join(args.out, f"{safe_name(url)}.png")
            rc, out, err = run(base + ["screenshot", "--full", png_path] + common, timeout=args.timeout)
            if rc != 0 or not os.path.exists(png_path):
                failed.append({"url": url, "error": f"screenshot failed: {err.strip() or out.strip()}"})
                continue
            rec["screenshot_file"] = png_path
            print(f"    已保存截图: {png_path}", file=sys.stderr)
        results.append(rec)

    # 4) 关闭（除非保留会话）
    if not args.no_close:
        run(base + ["close"] + common, timeout=args.timeout)

    summary = {
        "platform": args.platform,
        "session": args.session,
        "mode": args.mode,
        "results": results,
        "failed": failed,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
