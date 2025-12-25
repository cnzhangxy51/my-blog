#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务器端自动构建脚本（Python 版，Linux 推荐）

目标：你只需要 scp/sftp 往 docs/src/Notes/ 下传 md/图片等文件，服务器就自动：
1) npm run docs:build
2) 把 docs/.vitepress/dist 原子发布到 Nginx 目录（默认 /root/nginx/volumes/html/blog/dist）

依赖：
  pip install watchdog
以及：Node + npm、rsync（推荐）

可通过环境变量配置：
  WATCH_DIR         监听目录（默认：<repo>/docs/src/Notes）
  OUTPUT_DIR        Nginx dist 目录（默认：/root/nginx/volumes/html/blog/dist）
  DEBOUNCE_SECONDS  防抖秒数（默认：1）
  BUILD_CMD         构建命令（默认：npm run docs:build）
"""

from __future__ import annotations

import os
import sys
import time
import shutil
import subprocess
import threading
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except Exception as e:  # pragma: no cover
    print("[watch-build] 缺少依赖 watchdog，请先执行：pip install watchdog")
    print(f"[watch-build] 详情：{e}")
    sys.exit(1)


def _env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return v if v is not None and v != "" else default


ROOT_DIR = Path(__file__).resolve().parent.parent
WATCH_DIR = Path(_env("WATCH_DIR", str(ROOT_DIR / "docs" / "src" / "Notes"))).resolve()
OUTPUT_DIR = Path(_env("OUTPUT_DIR", "/root/nginx/volumes/html/blog/dist")).resolve()
DEBOUNCE_SECONDS = float(_env("DEBOUNCE_SECONDS", "1"))
BUILD_CMD = _env("BUILD_CMD", "npm run docs:build")

DIST_DIR = (ROOT_DIR / "docs" / ".vitepress" / "dist").resolve()

LOCK_FILE = Path(_env("LOCK_FILE", "/tmp/my-blog-docs-build.lock"))

IGNORED_BASENAMES = {
    ".DS_Store",
}

IGNORED_SUFFIXES = (
    ".swp",
    ".swx",
    ".swo",
    ".tmp",
    ".temp",
    "~",
)

IGNORED_EVENT_TYPES = {
    # 这些是“读文件”产生的事件：vitepress build 会大量读取 md/图片，导致刷屏/误触发
    "opened",
    "closed",
    "closed_no_write",
}


def _is_ignored_path(p: str) -> bool:
    # 忽略隐藏文件/目录，以及常见编辑器临时文件
    try:
        name = Path(p).name
    except Exception:
        return False
    if not name:
        return False
    if name in IGNORED_BASENAMES:
        return True
    if name.startswith("."):
        return True
    return any(name.endswith(s) for s in IGNORED_SUFFIXES)


class DebouncedBuilder:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None

    def trigger(self, reason: str, path: str) -> None:
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(DEBOUNCE_SECONDS, self._run_once)
            self._timer.daemon = True
            self._timer.start()
        print(f"[watch-build] 变更({reason})：{path} -> 已触发构建(防抖 {DEBOUNCE_SECONDS}s)")

    def _run_once(self) -> None:
        # Linux 下用文件锁防止并发构建（例如多个 watcher 或多次触发）
        try:
            import fcntl  # Linux only
        except Exception:
            fcntl = None  # type: ignore

        fp = None
        try:
            LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
            fp = open(LOCK_FILE, "w")
            if fcntl:
                try:
                    fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    print("[watch-build] 构建中，跳过本次触发")
                    return

            try:
                self.build_and_publish()
            except subprocess.CalledProcessError as e:
                print(f"[watch-build] 构建失败（exit={e.returncode}）：{e.cmd}")
                print(
                    "[watch-build] 提示：先在服务器仓库根目录执行 `npm ci` 或 `npm install`（不要用 --omit=dev/--production）。"
                )
            except Exception as e:
                print(f"[watch-build] 构建/发布异常：{e}")
        finally:
            if fp:
                try:
                    if fcntl:
                        fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass
                fp.close()

    def build_and_publish(self) -> None:
        print(f"[watch-build] {time.strftime('%F %T')} 开始构建...")
        subprocess.run(BUILD_CMD, cwd=str(ROOT_DIR), shell=True, check=True)

        if not DIST_DIR.exists():
            raise RuntimeError(f"dist 目录不存在：{DIST_DIR}")

        parent = OUTPUT_DIR.parent
        tmp_dir = Path(str(OUTPUT_DIR) + ".new")
        old_dir = Path(str(OUTPUT_DIR) + ".old")

        parent.mkdir(parents=True, exist_ok=True)
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)

        # 推荐使用 rsync（更快 + 支持 --delete）
        try:
            subprocess.run(
                ["rsync", "-a", "--delete", str(DIST_DIR) + "/", str(tmp_dir) + "/"],
                check=True,
            )
        except FileNotFoundError:
            # 没有 rsync 时退化成 copy（不会 delete 多余文件，建议还是装 rsync）
            print("[watch-build] 未检测到 rsync，退化为 shutil.copytree（建议安装 rsync）")
            shutil.rmtree(tmp_dir)
            shutil.copytree(DIST_DIR, tmp_dir)

        if old_dir.exists():
            shutil.rmtree(old_dir)
        if OUTPUT_DIR.exists():
            shutil.move(str(OUTPUT_DIR), str(old_dir))
        shutil.move(str(tmp_dir), str(OUTPUT_DIR))
        if old_dir.exists():
            shutil.rmtree(old_dir)

        print(f"[watch-build] {time.strftime('%F %T')} 发布完成：{OUTPUT_DIR}")


class NotesHandler(FileSystemEventHandler):
    def __init__(self, builder: DebouncedBuilder) -> None:
        self.builder = builder

    def on_any_event(self, event) -> None:  # noqa: ANN001
        # scp/sftp 常见行为：先写临时文件再 rename/move，所以只要 Notes 下有变化就触发
        # 排除一些无关事件可按需加（比如 .swp / .tmp），这里保持简单稳定。
        et = getattr(event, "event_type", "") or ""
        if et in IGNORED_EVENT_TYPES:
            return
        path = getattr(event, "src_path", "") or ""
        if _is_ignored_path(path):
            return
        self.builder.trigger(type(event).__name__, path)


def main() -> int:
    if not WATCH_DIR.exists():
        print(f"[watch-build] WATCH_DIR 不存在：{WATCH_DIR}")
        return 1

    if not (ROOT_DIR / "package.json").exists():
        print(f"[watch-build] 未找到 package.json，ROOT_DIR 可能不对：{ROOT_DIR}")
        return 1

    print(f"[watch-build] ROOT_DIR={ROOT_DIR}")
    print(f"[watch-build] WATCH_DIR={WATCH_DIR}")
    print(f"[watch-build] OUTPUT_DIR={OUTPUT_DIR}")
    print(f"[watch-build] DEBOUNCE_SECONDS={DEBOUNCE_SECONDS}")
    print(f"[watch-build] BUILD_CMD={BUILD_CMD}")
    print("[watch-build] 开始监听变更...")

    builder = DebouncedBuilder()
    handler = NotesHandler(builder)
    observer = Observer()
    observer.schedule(handler, str(WATCH_DIR), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[watch-build] 收到退出信号，正在停止...")
    finally:
        observer.stop()
        observer.join()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


