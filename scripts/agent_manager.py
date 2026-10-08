#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读书智能体 - 具名智能体管理器

面向"不懂命令行"的用户：他们说「创建一个读书智能体 xxx」，
AI 就跑本脚本建一个独立工作区；之后「用 xxx 帮我精读《孙子兵法》」，
AI 用 --project-dir 指到那个工作区跑流水线。

每个智能体 = 一个独立工作区，建在 `agents/<名字>/` 下，
有自己的书单和笔记，互不干扰。复制整个 skill 目录即可全部带走。

用法:
  python scripts/agent_manager.py create 兵哥读书 [--desc "给娃读历史"] [--books 0]
  python scripts/agent_manager.py list
  python scripts/agent_manager.py use 兵哥读书
  python scripts/agent_manager.py info 兵哥读书
  python scripts/agent_manager.py remove 兵哥读书 [--yes]

全局选项:
  --project-dir PATH   只用于定位 skill 根目录（默认: 本脚本的上级目录）
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

CST = timezone(timedelta(hours=8))

# 名字里不允许出现的字符（避免路径穿越与非法文件名）
ILLEGAL = set('/\\:*?"<>|\r\n\t')

AGENT_MD_TEMPLATE = """# 读书智能体 · {name}

{desc_line}
创建时间：{created}

## 你可以直接这么说

- 「用{name}帮我读《孙子兵法》」
- 「用{name}读一本」——按优先级自动挑一本没读过的
- 「用{name}读 3 本」
- 「给{name}加一本《{sample}》」
- 「{name}里有哪些书还没读」
- 「用{name}找一下上次读的《{sample}》笔记」

## 这个智能体的东西放在哪

```
{name}/
├── book_list.json                 你的书单（含每本书的笔记位置）
├── book_cache/book_raw_content/   精读笔记，一个个 HTML 文件
├── book_cache/book_meta/          每次选书的信息 + 联网核实过的事实清单
└── book_cache/book_log/           每次运行的日志
```

笔记是单个 HTML 文件，自带排版，可以直接发给别人看。

## 换电脑 / 备份

把 `{name}` 这个文件夹整个复制走就行，书单和笔记都在里面。
"""

CONFIG_TEMPLATE = {
    "version": "5.0",
    "book_list_path": "book_list.json",
    "output_dirs": {
        "book_meta": "book_cache/book_meta",
        "book_raw_content": "book_cache/book_raw_content",
        "push_result": "book_cache/push_result",
        "book_log": "book_cache/book_log",
    },
    "min_words": 15000,
    "target_words": 15000,
    "max_regenerate": 2,
    "selection_rules": {
        "priority_order": ["高", "中", "低"],
        "prefer_unread": True,
        "prefer_null_last_read": True,
    },
}


def resolve_skill_dir(explicit=None):
    """skill 根目录 = 本脚本所在目录的上一级"""
    if explicit:
        return Path(explicit).resolve()
    return Path(__file__).resolve().parent.parent


def agents_root(skill_dir):
    return skill_dir / "agents"


def safe_name(name):
    """校验并规范化智能体名字，返回 (ok, 名字或错误信息)"""
    n = (name or "").strip()
    if not n:
        return False, "智能体名字不能为空"
    if n in (".", ".."):
        return False, "智能体名字不能是 . 或 .."
    bad = [c for c in n if c in ILLEGAL]
    if bad:
        return False, f"名字里不能包含这些字符: {' '.join(sorted(set(bad)))}"
    if len(n) > 60:
        return False, "名字太长了（最多 60 个字符）"
    return True, n


def agent_dir(skill_dir, name):
    return agents_root(skill_dir) / name


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _count_books(agent_path):
    books = _read_json(agent_path / "book_list.json", [])
    if not isinstance(books, list):
        return 0, 0
    read = sum(1 for b in books if isinstance(b, dict) and b.get("last_read"))
    return len(books), read


def cmd_create(args, skill_dir):
    ok, name = safe_name(args.name)
    if not ok:
        print(json.dumps({"created": False, "error": name}, ensure_ascii=False, indent=2))
        return

    path = agent_dir(skill_dir, name)
    if path.exists():
        total, read = _count_books(path)
        print(json.dumps({
            "created": False,
            "exists": True,
            "name": name,
            "project_dir": str(path),
            "books": total,
            "read": read,
            "hint": "这个智能体已经存在了，直接用它读书即可；想重建请先 remove",
        }, ensure_ascii=False, indent=2))
        return

    now = datetime.now(CST)
    path.mkdir(parents=True, exist_ok=True)
    for sub in ("book_meta", "book_raw_content", "push_result", "book_log"):
        (path / "book_cache" / sub).mkdir(parents=True, exist_ok=True)

    _write_json(path / "book_list.json", [])
    _write_json(path / "book_config.json", CONFIG_TEMPLATE)
    _write_json(path / "agent.json", {
        "name": name,
        "desc": args.desc or "",
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "skill": "read-book-skill",
        "data_dir": ".",
    })

    (path / "AGENT.md").write_text(
        AGENT_MD_TEMPLATE.format(
            name=name,
            desc_line=(f"> {args.desc}" if args.desc else "> 一个帮你精读书的智能体。"),
            created=now.strftime("%Y-%m-%d %H:%M"),
            sample="穷查理宝典",
        ),
        encoding="utf-8",
    )

    print(json.dumps({
        "created": True,
        "name": name,
        "project_dir": str(path),
        "book_list": str(path / "book_list.json"),
        "books": 0,
        "next": f"后续命令加 --project-dir \"{path}\"",
        "hint": "书单目前是空的。用户说要读某本书时，用 ensure 命令把它加进书单再读。",
    }, ensure_ascii=False, indent=2))


def cmd_list(args, skill_dir):
    root = agents_root(skill_dir)
    rows = []
    if root.exists():
        for d in sorted(root.iterdir()):
            if not d.is_dir() or not (d / "book_list.json").exists():
                continue
            meta = _read_json(d / "agent.json", {}) or {}
            total, read = _count_books(d)
            rows.append({
                "name": d.name,
                "desc": meta.get("desc", ""),
                "created_at": meta.get("created_at", ""),
                "books": total,
                "read": read,
                "unread": total - read,
                "project_dir": str(d),
            })
    print(json.dumps({"total": len(rows), "agents": rows}, ensure_ascii=False, indent=2))


def _locate(args, skill_dir):
    ok, name = safe_name(args.name)
    if not ok:
        return None, None, {"found": False, "error": name}
    path = agent_dir(skill_dir, name)
    if not path.exists():
        existing = [d.name for d in sorted(agents_root(skill_dir).iterdir())
                    if d.is_dir() and (d / "book_list.json").exists()] if agents_root(skill_dir).exists() else []
        return None, None, {
            "found": False,
            "name": name,
            "existing": existing,
            "hint": "没有叫这个名字的读书智能体，先用 create 创建一个",
        }
    return name, path, None


def cmd_use(args, skill_dir):
    name, path, err = _locate(args, skill_dir)
    if err:
        print(json.dumps(err, ensure_ascii=False, indent=2))
        return
    total, read = _count_books(path)
    print(json.dumps({
        "found": True,
        "name": name,
        "project_dir": str(path),
        "book_list": str(path / "book_list.json"),
        "notes_dir": str(path / "book_cache" / "book_raw_content"),
        "books": total,
        "read": read,
        "unread": total - read,
        "flag": f'--project-dir "{path}"',
        "hint": "后面所有 book_manager / html_template / qc_check 命令都带上这个 flag",
    }, ensure_ascii=False, indent=2))


def cmd_info(args, skill_dir):
    name, path, err = _locate(args, skill_dir)
    if err:
        print(json.dumps(err, ensure_ascii=False, indent=2))
        return
    meta = _read_json(path / "agent.json", {}) or {}
    total, read = _count_books(path)
    notes = sorted(p.name for p in (path / "book_cache" / "book_raw_content").glob("*.html")) \
        if (path / "book_cache" / "book_raw_content").exists() else []
    books = _read_json(path / "book_list.json", []) or []
    print(json.dumps({
        "found": True,
        "name": name,
        "desc": meta.get("desc", ""),
        "created_at": meta.get("created_at", ""),
        "project_dir": str(path),
        "books": total,
        "read": read,
        "unread": total - read,
        "titles": [b.get("title", "") for b in books if isinstance(b, dict)],
        "note_files": notes,
        "note_count": len(notes),
    }, ensure_ascii=False, indent=2))


def cmd_remove(args, skill_dir):
    name, path, err = _locate(args, skill_dir)
    if err:
        err.update({"removed": False})
        print(json.dumps(err, ensure_ascii=False, indent=2))
        return

    total, _ = _count_books(path)
    note_dir = path / "book_cache" / "book_raw_content"
    note_count = len(list(note_dir.glob("*.html"))) if note_dir.exists() else 0

    if not args.yes:
        print(json.dumps({
            "removed": False,
            "require_confirm": True,
            "name": name,
            "will_remove_dir": str(path),
            "books": total,
            "notes": note_count,
            "hint": "这会连同书单和笔记一起删掉，不可恢复。确认后追加 --yes",
        }, ensure_ascii=False, indent=2))
        return

    shutil.rmtree(path)
    print(json.dumps({
        "removed": True,
        "name": name,
        "deleted_books": total,
        "deleted_notes": note_count,
    }, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="具名读书智能体管理")
    parser.add_argument("--project-dir", default=None,
                        help="skill 根目录（默认: 本脚本所在目录的上一级）")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("create", help="创建一个具名读书智能体")
    p.add_argument("name", help="智能体名字，如 兵哥读书")
    p.add_argument("--desc", default="", help="一句话说明")

    sub.add_parser("list", help="列出所有已创建的智能体")

    p = sub.add_parser("use", help="定位某个智能体，返回它的工作区路径")
    p.add_argument("name")

    p = sub.add_parser("info", help="查看某个智能体的详情")
    p.add_argument("name")

    p = sub.add_parser("remove", help="删除智能体（默认只预览）")
    p.add_argument("name")
    p.add_argument("--yes", action="store_true", help="确认删除")

    for _p in sub.choices.values():
        _p.add_argument("--project-dir", default=argparse.SUPPRESS,
                        help="skill 根目录（默认: 本脚本的上一级），放在命令前或后都行")

    args = parser.parse_args()
    skill_dir = resolve_skill_dir(args.project_dir)

    if args.command == "create":
        cmd_create(args, skill_dir)
    elif args.command == "list":
        cmd_list(args, skill_dir)
    elif args.command == "use":
        cmd_use(args, skill_dir)
    elif args.command == "info":
        cmd_info(args, skill_dir)
    elif args.command == "remove":
        cmd_remove(args, skill_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
