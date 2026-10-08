#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""read-book-skill 跨平台安装器

把本 skill 安装到本机所有支持的 AI 工具目录，一次装好到处可用。

用法:
  python install.py                # 安装到所有已检测到的位置
  python install.py --targets claude,openclaw   # 只装指定目标
  python install.py --list         # 只列出可安装目标，不实际安装
  python install.py --force        # 覆盖已有数据文件（默认保留用户的书单和笔记）

安全性:
  - 默认不覆盖已存在的用户数据（book_list.json / book_cache/ / notes 字段数据）
  - 只做复制，不删除任何东西
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

SKILL_NAME = "read-book-skill"

# 只安装这些，其余（.git / tests / examples / .idea / .workbuddy 等）一律不分发
CORE_ITEMS = ["SKILL.md", "scripts", "references", "assets", "install.py", "LICENSE", "README.md"]
# 用户数据：默认保留已有版本，不覆盖
DATA_ITEMS = ["book_list.json", "book_config.json", "book_cache"]
INSTALL_ITEMS = CORE_ITEMS + DATA_ITEMS

# 各平台的安装根目录。{home} 会被替换成用户主目录。
# 参考 Agent Skills 开放标准：`.agents/skills` 是覆盖面最广的通用路径
TARGETS = [
    ("agents", "{home}/.agents/skills", "通用总线（Cursor/Copilot/Gemini/Zed/OpenCode 等多数工具都读）"),
    ("claude", "{home}/.claude/skills", "Claude Code"),
    ("openclaw", "{home}/.openclaw/skills", "OpenClaw"),
    ("workbuddy", "{home}/.workbuddy/skills", "WorkBuddy"),
    ("codex", "{home}/.codex/skills", "Codex CLI"),
    ("gemini", "{home}/.gemini/skills", "Gemini CLI"),
    ("cursor", "{home}/.cursor/skills", "Cursor（用户级）"),
    ("opencode", "{home}/.config/opencode/skills", "OpenCode"),
]


def resolve_targets():
    home = str(Path.home())
    return [(key, path.replace("{home}", home), desc) for key, path, desc in TARGETS]


def must_exist(src_root):
    missing = [p for p in CORE_ITEMS if not (src_root / p).exists()]
    if missing:
        print(f"[ERROR] 源目录缺少必要内容: {missing}", file=sys.stderr)
        print(f"        请在 skill 根目录下运行本脚本: {src_root}", file=sys.stderr)
        sys.exit(1)


def copy_item(src, dst, keep_data):
    """复制单个文件或目录树，返回 (新增文件数, 跳过项数)。"""
    added = skipped = 0

    if keep_data and dst.exists() and src.name in DATA_ITEMS:
        return 0, 1

    if src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
        for item in sorted(src.iterdir()):
            if item.name in ("__pycache__", ".DS_Store"):
                continue
            a, s = copy_item(item, dst / item.name, keep_data)
            added += a
            skipped += s
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        added += 1
    return added, skipped


def copy_selected(src_root, dst, keep_data):
    """按白名单复制，避免把 tests/examples/.git/.workbuddy 等一并分发出去。"""
    added = skipped = 0
    for name in INSTALL_ITEMS:
        src = src_root / name
        if not src.exists():
            continue
        a, s = copy_item(src, dst / name, keep_data)
        added += a
        skipped += s
    return added, skipped


def do_install(src_root, key, dest_root, desc, keep_data):
    dest = dest_root / SKILL_NAME
    existed = dest.exists()
    dest.mkdir(parents=True, exist_ok=True)
    added, skipped = copy_selected(src_root, dest, keep_data)
    status = "更新" if existed else "安装"
    note = f"，保留 {skipped} 项已有数据" if skipped else ""
    print(f"  [OK] {key:10s} {status}成功 -> {dest}")
    print(f"             {desc}（新增/更新 {added} 个文件{note}）")
    return True


def main():
    parser = argparse.ArgumentParser(description="read-book-skill 跨平台安装器")
    parser.add_argument("--source", default=None, help="skill 源目录（默认: 本脚本所在目录）")
    parser.add_argument("--targets", default=None, help="逗号分隔的目标名，如 claude,openclaw")
    parser.add_argument("--list", action="store_true", help="只列出目标，不安装")
    parser.add_argument("--force", action="store_true", help="覆盖已有数据文件（默认保留）")
    args = parser.parse_args()

    src_root = Path(args.source).resolve() if args.source else Path(__file__).resolve().parent
    must_exist(src_root)

    all_targets = resolve_targets()
    if args.list:
        print("可安装目标：")
        for key, root, desc in all_targets:
            mark = "[已装]" if (Path(root) / SKILL_NAME).exists() else "[    ]"
            print(f"  {mark} {key:10s} {desc}")
            print(f"           {root}")
        return

    if args.targets:
        wanted = [t.strip() for t in args.targets.split(",")]
        all_targets = [t for t in all_targets if t[0] in wanted]
        if not all_targets:
            print(f"[ERROR] 没有匹配的目标: {wanted}", file=sys.stderr)
            print("        可用: " + ", ".join(k for k, _, _ in resolve_targets()))
            sys.exit(1)

    keep_data = not args.force
    print(f"源目录: {src_root}")
    print(f"数据策略: {'覆盖' if args.force else '保留已有书单与笔记'}\n")

    done = []
    for key, root, desc in all_targets:
        if not Path(root).parent.exists():
            print(f"  [--] {key:10s} 跳过（未检测到该工具的家目录: {Path(root).parent}）")
            continue
        if do_install(src_root, key, Path(root), desc, keep_data):
            done.append(key)

    print(f"\n完成。已安装到 {len(done)} 个位置: {', '.join(done) if done else '无'}")
    if done:
        print("\n下一步：新开一个会话（多数工具需重启才刷新 skill 列表），")
        print("然后直接说：帮我读一本《穷查理宝典》")
        print("\n卸载：删除对应目录下的 read-book-skill 文件夹即可。")


if __name__ == "__main__":
    main()
