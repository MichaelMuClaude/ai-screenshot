"""ai_screenshot.cli — full-screen screenshot tool for AI agents."""

from __future__ import annotations

import datetime
import os
import secrets
import shutil
import subprocess
import sys

from . import __version__


def setup_utf8_stdout() -> None:
    """在非UTF-8 locale(比如cron/systemd环境常见的LC_ALL=C)下,防止print()中文/emoji时崩溃。"""
    for stream in (sys.stdout, sys.stderr):
        if not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

# ── constants ────────────────────────────────────────────────────────────

CAPTURE_BIN = "import"                          # ImageMagick import, 已确认装在 /usr/bin/import
OUTPUT_DIR = os.path.expanduser("~/Pictures/screenshots")


def _timestamp_filename() -> str:
    """生成对文件系统安全且并发唯一的文件名。

    格式: screenshot-YYYY-MM-DDTHH-MM-SS-ffffff-XXXXXX.png
    - 用 '-' 替代时间里的 ':'（冒号在某些文件系统/工具下有问题）。
    - 微秒级时间戳消灭同秒碰撞。
    - 6 位十六进制随机后缀消灭同一微秒内的并发碰撞。
    """
    ts = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")
    suffix = secrets.token_hex(3)
    return f"screenshot-{ts}-{suffix}.png"


def _fail(message: str) -> int:
    """打印 [error] 前缀消息到 stderr，返回退出码 1。"""
    print(f"[error] {message}", file=sys.stderr)
    return 1


def capture() -> str | None:
    """执行一次全屏截图，返回落盘完整路径；失败返回 None。"""
    display = os.environ.get("DISPLAY")
    if not display:
        _fail("DISPLAY 环境变量未设置，无法截图（需要活动 X11 会话）")
        return None

    if not shutil.which(CAPTURE_BIN):
        _fail("找不到截图工具 import（ImageMagick），请先安装：sudo apt install imagemagick")
        return None

    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    except PermissionError:
        _fail(f"无法写入截图目录 {OUTPUT_DIR}（权限不足）")
        return None

    path = os.path.join(OUTPUT_DIR, _timestamp_filename())

    result = subprocess.run(
        [CAPTURE_BIN, "-window", "root", path],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        detail = result.stderr.strip() if result.stderr else "无 stderr 输出"
        _fail(f"截图失败：import 退出码 {result.returncode}（{detail}）")
        return None

    if not os.path.exists(path) or os.path.getsize(path) == 0:
        _fail(f"截图似乎成功但输出文件无效（空或不存在）：{path}")
        return None

    return path


def main() -> int:
    setup_utf8_stdout()
    path = capture()
    if path is None:
        return 1
    print(path)      # 唯一的 stdout 输出：完整落盘路径
    return 0


if __name__ == "__main__":
    sys.exit(main())
