#!/usr/bin/env python3
"""读书智能体 - 书籍管理脚本（可移植版）

支持 --project-dir 指定项目根目录，默认为脚本上级目录。

Usage:
  python book_manager.py select                     # 按优先级选一本未读的书
  python book_manager.py select --title "书名"        # 指定书名选书
  python book_manager.py select --random             # 随机选一本
  python book_manager.py update "书名"                # 更新 last_read 为今天
  python book_manager.py list --category "投资"        # 按分类列出
  python book_manager.py list --priority 高          # 按优先级列出
  python book_manager.py search "关键词"              # 搜索书名/作者
  python book_manager.py stats                       # 统计信息
  python book_manager.py unread                      # 列出所有未读书
  python book_manager.py add "书名" --author "作者"   # 添加新书
  python book_manager.py remove "书名"               # 删除书籍

全局选项:
  --project-dir PATH   项目根目录（默认: 脚本上级目录）
"""

import json
import sys
import os
import shutil
import argparse
import random
import subprocess
from datetime import datetime, timezone, timedelta

# 时区
CST = timezone(timedelta(hours=8))


def resolve_project_dir(explicit=None):
    """解析项目根目录"""
    if explicit:
        return os.path.abspath(explicit)
    # 默认: 脚本上级目录
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_book_list_path(project_dir):
    return os.path.join(project_dir, "book_list.json")


def get_log_dir(project_dir):
    return os.path.join(project_dir, "book_cache", "book_log")


CACHE_SUBDIRS = [
    "book_cache/book_meta",
    "book_cache/book_raw_content",
    "book_cache/push_result",
    "book_cache/book_log",
]


def ensure_project(project_dir):
    """零初始化：书单/配置/缓存目录不存在就自动建空的。

    不塞任何示例书 —— 用户的书单只应该有他自己加的书。
    返回本次新建的东西（已存在则返回空列表）。
    """
    created = []
    if not os.path.isdir(project_dir):
        os.makedirs(project_dir, exist_ok=True)
        created.append(project_dir)

    bl = get_book_list_path(project_dir)
    if not os.path.exists(bl):
        save_books(project_dir, [])
        created.append("book_list.json")

    cfg = os.path.join(project_dir, "book_config.json")
    if not os.path.exists(cfg):
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "book_config.json")
        src = os.path.normpath(src)
        if os.path.exists(src):
            try:
                with open(src, "r", encoding="utf-8") as f:
                    json.load(f)
                shutil.copy2(src, cfg)
                created.append("book_config.json")
            except (json.JSONDecodeError, OSError):
                pass

    for d in CACHE_SUBDIRS:
        p = os.path.join(project_dir, *d.split("/"))
        if not os.path.isdir(p):
            os.makedirs(p, exist_ok=True)
            created.append(d)
    return created


def load_books(project_dir):
    path = get_book_list_path(project_dir)
    if not os.path.exists(path):
        # 零初始化：第一次用的时候自动建一份空书单，而不是报错
        ensure_project(project_dir)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"书单JSON格式错误: {e}", "file": path}, ensure_ascii=False))
        sys.exit(1)


def save_books(project_dir, books):
    path = get_book_list_path(project_dir)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)


def today_str():
    return datetime.now(CST).strftime("%Y-%m-%d")


def now_ts():
    return datetime.now(CST).strftime("%Y%m%d_%H%M%S")


def priority_weight(p):
    return {"高": 0, "中": 1, "低": 2}.get(p, 3)


def select_book(books, title=None, random_pick=False):
    """选书逻辑：优先级 高>中>低, 优先 last_read 为空的"""
    if not books:
        return None

    if title:
        matches = [b for b in books if title in b.get("title", "")]
        if matches:
            return matches[0]
        return None

    # 先按 last_read 为空筛选（未读书）
    unread = [b for b in books if not b.get("last_read")]

    if random_pick:
        # 随机选书：优先从未读中选，全部已读则从所有书中选
        pool = unread if unread else books
        return random.choice(pool)

    # 按优先级自动选
    if unread:
        unread.sort(key=lambda b: priority_weight(b.get("priority", "")))
        return unread[0]

    # 全部有日期 -> 取日期最早的
    books_sorted = sorted(
        books,
        key=lambda b: (b.get("last_read") or "0000-00-00", priority_weight(b.get("priority", "")))
    )
    return books_sorted[0]


def match_books(books, title):
    """将书名解析为 (精确匹配索引, 模糊匹配索引)。

    精确 = 书名完全相同；模糊 = 书名包含输入的关键词。
    分开返回是为了让命令层能实现"精确优先"策略，
    避免 update/remove "原则" 时静默波及《原则生活》。
    """
    exact, fuzzy = [], []
    for i, b in enumerate(books):
        t = b.get("title", "")
        if t == title:
            exact.append(i)
        elif title in t:
            fuzzy.append(i)
    return exact, fuzzy


def _resolve_targets(books, title, allow_all=False):
    """按"精确优先"解析操作目标，返回 (indexes, error_payload)。

    - 有精确匹配     -> 只作用于精确匹配的书
    - 无精确、1 个模糊 -> 作用于该本
    - 无精确、多个模糊 -> 拒绝执行并列出候选，除非 allow_all
    """
    exact, fuzzy = match_books(books, title)
    if exact:
        return exact, None
    if len(fuzzy) == 1:
        return fuzzy, None
    if len(fuzzy) > 1:
        if allow_all:
            return fuzzy, None
        return None, {
            "error": "模糊匹配到多本书，已拒绝执行",
            "input": title,
            "matches": [books[i].get("title", "") for i in fuzzy],
            "hint": "请输入更完整的书名精确定位",
        }
    return None, {"error": "未找到匹配书籍", "input": title}


def update_last_read(books, title):
    """更新指定书的 last_read 为今天"""
    updated = 0
    for b in books:
        if title in b["title"] or b["title"] == title:
            b["last_read"] = today_str()
            b["user_read"] = True
            updated += 1
    return updated


def write_log(project_dir, task_id, book, status, extra=""):
    log_dir = get_log_dir(project_dir)
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{task_id}.log")
    ts = datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"[{ts}] Task: {task_id}",
        f"  Book: {book.get('title', 'N/A')}",
        f"  Author: {book.get('author', 'N/A')}",
        f"  Status: {status}",
    ]
    if extra:
        lines.append(f"  Detail: {extra}")
    lines.append("")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return log_file


def to_slug(title):
    """生成文件名安全的 slug

    策略：保留ASCII字母数字、将中文字符转为下划线、清理多余符号。
    建议：用户手动在 book_list.json 中填写 en_slug 字段以获得更好的拼音slug。
    """
    import re
    if not title:
        return ""
    # 保留ASCII字母数字和连字符，其他字符转下划线
    slug = re.sub(r'[^a-zA-Z0-9\-]', '_', title)
    # 清理连续下划线和首尾下划线
    slug = re.sub(r'_+', '_', slug).strip('_')
    if not slug:
        # 全是中文字符时，返回单个下划线
        return "_"
    return slug.lower()


def add_book(books, title, author="", priority="中", tags=None, en_slug=""):
    """添加新书到书单"""
    if tags is None:
        tags = []
    book = {
        "title": title,
        "author": author,
        "priority": priority,
        "tags": tags,
        "en_slug": en_slug or title,
        "user_read": False,
        "last_read": None
    }
    books.append(book)
    return book


def cmd_select(args, project_dir):
    books = load_books(project_dir)
    if not books:
        print(json.dumps({
            "error": "书单是空的，没有书可读",
            "total": 0,
            "hint": "用 ensure 把用户说的那本书直接加进来：ensure \"书名\" --project-dir <项目目录>，然后继续精读"
        }, ensure_ascii=False))
        return
    book = select_book(books, title=args.title, random_pick=args.random)
    if book is None:
        print(json.dumps({"error": "未找到匹配书籍"}, ensure_ascii=False))
        return
    result = {
        "selected": True,
        "title": book["title"],
        "author": book.get("author", ""),
        "priority": book.get("priority", ""),
        "tags": book.get("tags", []),
        "last_read": book.get("last_read"),
        "en_slug": book.get("en_slug", ""),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_update(args, project_dir):
    books = load_books(project_dir)
    targets, err = _resolve_targets(books, args.title, allow_all=args.all)
    if err:
        err.update({"updated": False})
        print(json.dumps(err, ensure_ascii=False, indent=2))
        return

    date = today_str()
    note_rel = None
    if args.note_path:
        # 相对路径必须相对「项目根目录」解析，不能相对当前工作目录。
        # 具名智能体场景下 AI 通常在 skill 根目录执行命令，而数据在 agents/<名字>/ 下，
        # 若按 CWD 解析会算出 ../../book_cache/... 这种越界路径，笔记从此失联。
        raw = args.note_path
        if os.path.isabs(raw):
            abs_note = os.path.normpath(raw)
        else:
            abs_note = os.path.normpath(os.path.join(project_dir, raw))
            if not os.path.exists(abs_note):
                # 兜底：万一传的是相对当前工作目录的写法，且那边确实有这个文件
                alt = os.path.normpath(os.path.abspath(raw))
                if os.path.exists(alt):
                    abs_note = alt
        try:
            note_rel = os.path.relpath(abs_note, project_dir).replace("\\", "/")
        except ValueError:
            note_rel = abs_note.replace("\\", "/")

    titles = []
    for i in targets:
        books[i]["last_read"] = date
        books[i]["user_read"] = True
        if note_rel:
            # 幂等：同一个 task_id / 同一条路径只保留一条，避免重跑时越堆越多
            task_id = os.path.splitext(os.path.basename(note_rel))[0]
            notes = books[i].setdefault("notes", [])
            hit = next((n for n in notes
                        if n.get("task_id") == task_id or n.get("path") == note_rel), None)
            if hit is not None:
                hit.update({"task_id": task_id, "path": note_rel, "date": date})
            else:
                notes.append({"task_id": task_id, "path": note_rel, "date": date})
        titles.append(books[i].get("title", ""))
    save_books(project_dir, books)

    result = {
        "updated": True,
        "titles": titles,
        "count": len(titles),
        "date": date,
    }
    if len(titles) > 1:
        result["warning"] = f"本次同时更新了 {len(titles)} 本书，确认是否符合预期"
    if note_rel:
        result["note_recorded"] = note_rel
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_list(args, project_dir):
    books = load_books(project_dir)
    filtered = books
    if args.category:
        filtered = [b for b in filtered if args.category in (b.get("tags") or [])]
    if args.priority:
        filtered = [b for b in filtered if b.get("priority") == args.priority]
    if args.unread:
        filtered = [b for b in filtered if not b.get("last_read")]
    def _row(b):
        ns = sorted((b.get("notes") or []),
                    key=lambda n: ((n.get("date") or ""), (n.get("task_id") or "")))
        latest = ns[-1] if ns else None
        note_path = latest.get("path", "") if latest else ""
        return {
            "title": b.get("title", ""),
            "author": b.get("author", ""),
            "priority": b.get("priority", ""),
            "tags": b.get("tags", []),
            "last_read": b.get("last_read"),
            "status": "已读" if b.get("last_read") else "未读",
            "notes": len(ns),
            "has_note": bool(ns),
            "note_path": note_path,
            "note_exists": os.path.exists(_note_abs(project_dir, note_path)) if note_path else False,
        }

    rows = [_row(b) for b in filtered]
    result = {
        "total": len(rows),
        "with_notes": sum(1 for r in rows if r["has_note"]),
        "books": rows,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_search(args, project_dir):
    books = load_books(project_dir)
    kw = args.keyword
    results = [b for b in books if kw in b.get("title", "") or kw in b.get("author", "")]
    result = {
        "keyword": kw,
        "total": len(results),
        "books": [{
            "title": b.get("title", ""),
            "author": b.get("author", ""),
            "priority": b.get("priority", ""),
            "tags": b.get("tags", []),
            "last_read": b.get("last_read"),
            "status": "已读" if b.get("last_read") else "未读"
        } for b in results]
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_stats(args, project_dir):
    books = load_books(project_dir)
    from collections import Counter
    total = len(books)
    read = sum(1 for b in books if b.get("last_read"))
    unread = total - read
    prio = dict(Counter(b.get("priority", "") for b in books))
    tags = Counter()
    for b in books:
        for t in b.get("tags", []):
            tags[t] += 1
    result = {
        "total": total,
        "read": read,
        "unread": unread,
        "read_percentage": f"{read*100//total if total else 0}%",
        "priority_distribution": prio,
        "top_tags": dict(tags.most_common(10))
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_unread(args, project_dir):
    books = load_books(project_dir)
    unread = [b for b in books if not b.get("last_read")]
    unread.sort(key=lambda b: priority_weight(b.get("priority", "")))
    result = {
        "total": len(unread),
        "books": [{
            "title": b.get("title", ""),
            "author": b.get("author", ""),
            "priority": b.get("priority", ""),
            "tags": b.get("tags", [])
        } for b in unread]
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_add(args, project_dir):
    books = load_books(project_dir)

    title = args.title.strip()
    if not title:
        print(json.dumps({"added": False, "error": "书名不能为空"}, ensure_ascii=False, indent=2))
        return

    if not args.force:
        same_name = [b for b in books if b.get("title") == title]
        if same_name:
            ex = same_name[0]
            print(json.dumps({
                "added": False,
                "duplicate": True,
                "title": title,
                "existing": {
                    "title": ex.get("title"),
                    "author": ex.get("author"),
                    "priority": ex.get("priority"),
                    "last_read": ex.get("last_read"),
                },
                "hint": "书单中已有同名书籍，确认是另一本则加 --force",
            }, ensure_ascii=False, indent=2))
            return

    book = add_book(books, title, author=args.author, priority=args.priority,
                    tags=args.tags.split(",") if args.tags else [])
    save_books(project_dir, books)
    print(json.dumps({"added": True, "book": book}, ensure_ascii=False, indent=2))


def cmd_ensure(args, project_dir):
    """确保某本书在书单里：有就取出来，没有就加进去。

    这是"用户点名要读某本书"这条路径的入口 —— 用户想读的书
    十有八九不在书单里（比如刚创建的智能体书单是空的）。
    没有它就只能让 AI 自己拼 add + select 两步，容易重复添加或书名对不上。
    """
    books = load_books(project_dir)
    title = (args.title or "").strip()
    if not title:
        print(json.dumps({"ok": False, "error": "书名不能为空"}, ensure_ascii=False, indent=2))
        return

    exact, fuzzy = match_books(books, title)

    if exact:
        b = books[exact[0]]
        print(json.dumps({
            "ok": True, "existed": True, "book": b,
            "title": b.get("title"), "author": b.get("author"),
            "priority": b.get("priority"), "tags": b.get("tags", []),
            "last_read": b.get("last_read"), "en_slug": b.get("en_slug", ""),
        }, ensure_ascii=False, indent=2))
        return

    if len(fuzzy) == 1:
        b = books[fuzzy[0]]
        print(json.dumps({
            "ok": True, "existed": True, "fuzzy": True,
            "input": title, "matched": b.get("title"),
            "book": b,
            "title": b.get("title"), "author": b.get("author"),
            "priority": b.get("priority"), "tags": b.get("tags", []),
            "last_read": b.get("last_read"), "en_slug": b.get("en_slug", ""),
            "hint": "书单里已有近似书名，已按它继续；确认是另一本请用完整书名",
        }, ensure_ascii=False, indent=2))
        return

    if len(fuzzy) > 1:
        print(json.dumps({
            "ok": False, "existed": False,
            "error": "书单里有多本近似书名，无法确定是哪本",
            "input": title,
            "matches": [books[i].get("title", "") for i in fuzzy],
            "hint": "请用完整书名重试",
        }, ensure_ascii=False, indent=2))
        return

    # 确实没有 -> 新建
    book = add_book(books, title, author=args.author,
                    priority=args.priority,
                    tags=args.tags.split(",") if args.tags else [])
    # 未显式指定作者时，slug 至少不是整段中文
    save_books(project_dir, books)
    print(json.dumps({
        "ok": True, "existed": False, "added": True,
        "book": book,
        "title": book.get("title"), "author": book.get("author"),
        "priority": book.get("priority"), "tags": book.get("tags", []),
        "last_read": book.get("last_read"), "en_slug": book.get("en_slug", ""),
        "hint": "这本书原本不在书单里，已自动加入后继续精读",
    }, ensure_ascii=False, indent=2))


def cmd_remove(args, project_dir):
    """删除书籍。

    默认只预览不删除（避免 'remove 原则' 连带删掉《原则生活》却事后才告知），
    必须显式加 --yes 才真正删除。
    """
    books = load_books(project_dir)
    targets, err = _resolve_targets(books, args.title, allow_all=args.all)
    if err:
        err.update({"removed": False})
        print(json.dumps(err, ensure_ascii=False, indent=2))
        return

    targets = sorted(targets)
    doomed = [books[i].get("title", "") for i in targets]

    if not args.yes:
        print(json.dumps({
            "removed": False,
            "require_confirm": True,
            "will_remove": doomed,
            "count": len(doomed),
            "hint": "确认无误后追加 --yes 执行删除",
        }, ensure_ascii=False, indent=2))
        return

    for i in reversed(targets):
        del books[i]
    save_books(project_dir, books)
    print(json.dumps({
        "removed": True,
        "titles": doomed,
        "count": len(doomed),
        "remaining": len(books),
    }, ensure_ascii=False, indent=2))


VALID_PRIORITIES = ("高", "中", "低")


def cmd_edit(args, project_dir):
    """修改已有书籍的信息（书名/作者/优先级/标签）。"""
    books = load_books(project_dir)
    targets, err = _resolve_targets(books, args.title, allow_all=False)
    if err:
        err.update({"edited": False})
        print(json.dumps(err, ensure_ascii=False, indent=2))
        return
    if len(targets) != 1:
        print(json.dumps({"edited": False, "error": "一次只能修改一本书"}, ensure_ascii=False, indent=2))
        return

    idx = targets[0]
    book = books[idx]
    changes = {}

    if args.new_title is not None:
        new_title = args.new_title.strip()
        if not new_title:
            print(json.dumps({"edited": False, "error": "新书名不能为空"}, ensure_ascii=False, indent=2))
            return
        if any(i != idx and books[i].get("title") == new_title for i in range(len(books))):
            print(json.dumps({"edited": False, "error": f"已存在同名书籍《{new_title}》"},
                             ensure_ascii=False, indent=2))
            return
        changes["title"] = {"from": book.get("title"), "to": new_title}
        book["title"] = new_title

    if args.author is not None:
        changes["author"] = {"from": book.get("author"), "to": args.author}
        book["author"] = args.author

    if args.priority is not None:
        if args.priority not in VALID_PRIORITIES:
            print(json.dumps({"edited": False, "error": f"优先级只能是 {'/'.join(VALID_PRIORITIES)}"},
                             ensure_ascii=False, indent=2))
            return
        changes["priority"] = {"from": book.get("priority"), "to": args.priority}
        book["priority"] = args.priority

    if args.tags is not None:
        new_tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        changes["tags"] = {"from": book.get("tags"), "to": new_tags}
        book["tags"] = new_tags

    if args.add_tags:
        current = list(book.get("tags") or [])
        for t in args.add_tags.split(","):
            t = t.strip()
            if t and t not in current:
                current.append(t)
        changes["tags"] = {"from": book.get("tags"), "to": current}
        book["tags"] = current

    if not changes:
        print(json.dumps({
            "edited": False,
            "error": "没有指定任何要修改的字段",
            "title": book.get("title"),
            "available": ["--new-title", "--author", "--priority", "--tags", "--add-tags"],
        }, ensure_ascii=False, indent=2))
        return

    save_books(project_dir, books)
    print(json.dumps({"edited": True, "title": book.get("title"), "changes": changes},
                     ensure_ascii=False, indent=2))


def cmd_notes(args, project_dir):
    """列出已生成的精读笔记，支持按书名过滤。"""
    books = load_books(project_dir)
    rows = []
    for b in books:
        for n in (b.get("notes") or []):
            p = n.get("path", "")
            rows.append({
                "title": b.get("title", ""),
                "author": b.get("author", ""),
                "date": n.get("date"),
                "task_id": n.get("task_id"),
                "path": p,
                "exists": os.path.exists(os.path.join(project_dir, p)) if p else False,
            })
    if args.title:
        rows = [r for r in rows if args.title in r["title"]]

    missing = sum(1 for r in rows if not r["exists"])
    print(json.dumps({
        "total": len(rows),
        "missing_files": missing,
        "notes": rows,
    }, ensure_ascii=False, indent=2))


def _note_abs(project_dir, rel):
    """笔记相对路径 -> 绝对路径（相对路径按 project_dir 解析）。"""
    if not rel:
        return ""
    if os.path.isabs(rel):
        return os.path.normpath(rel)
    p = os.path.normpath(os.path.join(project_dir, rel))
    if not os.path.exists(p):
        alt = os.path.normpath(os.path.abspath(rel))
        if os.path.exists(alt):
            return alt
    return p


def _open_file(path):
    """用系统默认程序打开文件，返回 (ok, error)。"""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True, ""
    except Exception as e:
        return False, str(e)


def _collect_notes(books, project_dir, indexes=None):
    """收集笔记记录，按时间升序。indexes 为 None 时收集全部。"""
    rows = []
    for i, b in enumerate(books):
        if indexes is not None and i not in indexes:
            continue
        for n in (b.get("notes") or []):
            rel = n.get("path", "")
            abs_p = _note_abs(project_dir, rel)
            rows.append({
                "title": b.get("title", ""),
                "author": b.get("author", ""),
                "date": n.get("date"),
                "task_id": n.get("task_id"),
                "path": rel,
                "abs_path": abs_p,
                "exists": os.path.exists(abs_p) if rel else False,
            })
    rows.sort(key=lambda r: ((r.get("date") or ""), (r.get("task_id") or "")))
    return rows


def cmd_open(args, project_dir):
    """打开某本书的精读笔记（HTML）。

    用户说"帮我打开《xxx》的读书笔记"时直接用这条：
    定位书 -> 找到最新一篇笔记 -> 确认文件还在 -> 用系统默认浏览器打开。
    """
    books = load_books(project_dir)
    title = (args.title or "").strip()

    if not books:
        print(json.dumps({
            "ok": False, "error": "书单是空的，没有任何笔记",
            "total_books": 0,
            "hint": "先加书：add \"书名\"，或让它读一本：ensure \"书名\""
        }, ensure_ascii=False, indent=2))
        return

    if title:
        indexes, err = _resolve_targets(books, title, allow_all=args.all)
        if err:
            err = dict(err)
            err["ok"] = False
            if err.get("error") == "未找到匹配书籍":
                err["hint"] = ("书单里没有这本书。先加进书单（add \"书名\"）再读，"
                               "或者用 list 看看书单里都有什么")
            else:
                err["hint"] = err.get("hint") or "说清楚是哪本书，或用 list 看看书单里都有什么"
            print(json.dumps(err, ensure_ascii=False, indent=2))
            return
    else:
        indexes = None  # 没点名 -> 在全部笔记里找最新一篇

    rows = _collect_notes(books, project_dir, indexes)

    if not rows:
        payload = {"ok": False, "error": "这本书还没有精读笔记", "input": title}
        if title and indexes:
            b = books[indexes[0]]
            payload["title"] = b.get("title", "")
            payload["status"] = "已读" if b.get("last_read") else "未读"
        payload["hint"] = "要现在读吗？读完整条流水线后会生成 HTML 笔记，再打开就能看到"
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    # 多篇笔记且点名了多本书 -> 不猜，列出来
    titles = sorted({r["title"] for r in rows})
    if len(titles) > 1 and not args.latest:
        print(json.dumps({
            "ok": False,
            "error": "有多本书都匹配，不确定要打开哪本",
            "input": title,
            "candidates": titles,
            "hint": "说完整书名，或加 --latest 直接打开最近的一篇",
        }, ensure_ascii=False, indent=2))
        return

    target = rows[-1]
    idx = args.index if args.index is not None else None
    if idx is not None:
        if 0 <= idx < len(rows):
            target = rows[idx]
        else:
            print(json.dumps({
                "ok": False, "error": f"没有第 {idx + 1} 篇笔记",
                "total_notes": len(rows), "notes": rows,
            }, ensure_ascii=False, indent=2))
            return

    if not target["exists"]:
        print(json.dumps({
            "ok": False, "error": "笔记文件不在了（可能被移动或删除）",
            "title": target["title"], "path": target["path"],
            "abs_path": target["abs_path"],
            "hint": "重新读一遍会生成新的笔记文件",
        }, ensure_ascii=False, indent=2))
        return

    opened, open_err = (False, "")
    if not args.no_open:
        opened, open_err = _open_file(target["abs_path"])

    print(json.dumps({
        "ok": True,
        "opened": opened,
        "title": target["title"],
        "author": target["author"],
        "date": target["date"],
        "task_id": target["task_id"],
        "path": target["path"],
        "abs_path": target["abs_path"],
        "open_error": open_err or None,
        "total_notes": len(rows),
        "notes": rows,
        "hint": ("已用默认浏览器打开" if opened else
                 "文件在下面这个路径，直接打开即可") + "。把这个路径告诉用户。",
    }, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="读书智能体书籍管理")
    parser.add_argument("--project-dir", default=None, help="项目根目录（默认: 脚本上级目录）")
    sub = parser.add_subparsers(dest="command")

    p_sel = sub.add_parser("select", help="选书")
    p_sel.add_argument("--title", default=None, help="指定书名")
    p_sel.add_argument("--random", action="store_true", help="随机选")

    p_upd = sub.add_parser("update", help="更新阅读状态（精确优先，命中多本会拒绝）")
    p_upd.add_argument("title", help="书名（完整书名可精确定位）")
    p_upd.add_argument("--all", action="store_true", help="模糊命中多本时全部更新")
    p_upd.add_argument("--note-path", default=None, help="精读笔记HTML路径，回写到书单")

    p_lst = sub.add_parser("list", help="列出书籍")
    p_lst.add_argument("--category", default=None)
    p_lst.add_argument("--priority", default=None)
    p_lst.add_argument("--unread", action="store_true")

    p_srch = sub.add_parser("search", help="搜索")
    p_srch.add_argument("keyword")

    sub.add_parser("stats", help="统计")
    sub.add_parser("unread", help="未读书列表")

    p_add = sub.add_parser("add", help="添加新书")
    p_add.add_argument("title", help="书名")
    p_add.add_argument("--author", default="", help="作者")
    p_add.add_argument("--priority", default="中", help="优先级 高/中/低")
    p_add.add_argument("--tags", default="", help="标签，逗号分隔")
    p_add.add_argument("--force", action="store_true", help="同名时仍强制添加")

    p_ensure = sub.add_parser("ensure", help="确保某本书在书单里（不在就加入，然后返回它）")
    p_ensure.add_argument("title", help="书名")
    p_ensure.add_argument("--author", default="", help="作者（新建时用）")
    p_ensure.add_argument("--priority", default="中", help="优先级 高/中/低（新建时用）")
    p_ensure.add_argument("--tags", default="", help="标签，逗号分隔（新建时用）")

    p_edit = sub.add_parser("edit", help="修改书籍信息")
    p_edit.add_argument("title", help="要修改的书名")
    p_edit.add_argument("--new-title", default=None, help="新书名")
    p_edit.add_argument("--author", default=None, help="新作者")
    p_edit.add_argument("--priority", default=None, help="新优先级 高/中/低")
    p_edit.add_argument("--tags", default=None, help="重设标签，逗号分隔")
    p_edit.add_argument("--add-tags", default=None, help="追加标签，逗号分隔")

    p_rm = sub.add_parser("remove", help="删除书籍（需二次确认）")
    p_rm.add_argument("title", help="书名")
    p_rm.add_argument("--yes", action="store_true", help="确认删除，不加则只预览")
    p_rm.add_argument("--all", action="store_true", help="模糊命中多本时全部删除")

    p_notes = sub.add_parser("notes", help="列出精读笔记")
    p_notes.add_argument("--title", default=None, help="按书名过滤")

    p_open = sub.add_parser("open", help="打开某本书的精读笔记（用系统默认程序）")
    p_open.add_argument("title", nargs="?", default=None, help="书名；省略则打开最近的一篇笔记")
    p_open.add_argument("--latest", action="store_true", help="命中多本时直接打开最近的一篇")
    p_open.add_argument("--index", type=int, default=None, help="打开第 N 篇（从 0 开始）")
    p_open.add_argument("--all", action="store_true", help="模糊命中多本时一并考虑")
    p_open.add_argument("--no-open", action="store_true", help="只返回路径，不真的打开")

    # --project-dir 同时挂到每个子命令上：位置可前可后。
    # 不这么做的话，`update "书名" --project-dir X`（子命令在前）会直接报
    # unrecognized arguments —— 而那正是文档里的写法。
    # default=SUPPRESS 保证子命令没带该参数时不会把主 parser 的值覆盖成 None。
    for _p in sub.choices.values():
        _p.add_argument("--project-dir", default=argparse.SUPPRESS,
                        help="项目根目录（默认: skill 根目录），放在命令前或后都行")

    args = parser.parse_args()
    project_dir = resolve_project_dir(args.project_dir)

    if args.command == "select":
        cmd_select(args, project_dir)
    elif args.command == "update":
        cmd_update(args, project_dir)
    elif args.command == "list":
        cmd_list(args, project_dir)
    elif args.command == "search":
        cmd_search(args, project_dir)
    elif args.command == "stats":
        cmd_stats(args, project_dir)
    elif args.command == "unread":
        cmd_unread(args, project_dir)
    elif args.command == "add":
        cmd_add(args, project_dir)
    elif args.command == "edit":
        cmd_edit(args, project_dir)
    elif args.command == "ensure":
        cmd_ensure(args, project_dir)
    elif args.command == "remove":
        cmd_remove(args, project_dir)
    elif args.command == "notes":
        cmd_notes(args, project_dir)
    elif args.command == "open":
        cmd_open(args, project_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
