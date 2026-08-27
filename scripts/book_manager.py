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
import argparse
import random
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


def load_books(project_dir):
    path = get_book_list_path(project_dir)
    if not os.path.exists(path):
        print(json.dumps({"error": f"书单文件不存在: {path}", "hint": "运行 init_project.py 初始化项目，或手动创建 book_list.json"}, ensure_ascii=False))
        sys.exit(1)
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
    count = update_last_read(books, args.title)
    if count > 0:
        save_books(project_dir, books)
        print(json.dumps({"updated": True, "title": args.title, "count": count, "date": today_str()}, ensure_ascii=False))
    else:
        print(json.dumps({"updated": False, "title": args.title, "error": "未找到匹配书籍"}, ensure_ascii=False))


def cmd_list(args, project_dir):
    books = load_books(project_dir)
    filtered = books
    if args.category:
        filtered = [b for b in filtered if args.category in (b.get("tags") or [])]
    if args.priority:
        filtered = [b for b in filtered if b.get("priority") == args.priority]
    if args.unread:
        filtered = [b for b in filtered if not b.get("last_read")]
    result = {
        "total": len(filtered),
        "books": [{
            "title": b.get("title", ""),
            "author": b.get("author", ""),
            "priority": b.get("priority", ""),
            "tags": b.get("tags", []),
            "last_read": b.get("last_read"),
            "status": "已读" if b.get("last_read") else "未读"
        } for b in filtered]
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
    book = add_book(books, args.title, author=args.author, priority=args.priority, tags=args.tags.split(",") if args.tags else [])
    save_books(project_dir, books)
    print(json.dumps({"added": True, "book": book}, ensure_ascii=False, indent=2))


def cmd_remove(args, project_dir):
    books = load_books(project_dir)
    before = len(books)
    books = [b for b in books if args.title not in b["title"]]
    after = len(books)
    save_books(project_dir, books)
    print(json.dumps({"removed": True, "count": before - after}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="读书智能体书籍管理")
    parser.add_argument("--project-dir", default=None, help="项目根目录（默认: 脚本上级目录）")
    sub = parser.add_subparsers(dest="command")

    p_sel = sub.add_parser("select", help="选书")
    p_sel.add_argument("--title", default=None, help="指定书名")
    p_sel.add_argument("--random", action="store_true", help="随机选")

    p_upd = sub.add_parser("update", help="更新阅读状态")
    p_upd.add_argument("title", help="书名(支持模糊匹配)")

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

    p_rm = sub.add_parser("remove", help="删除书籍")
    p_rm.add_argument("title", help="书名(支持模糊匹配)")

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
    elif args.command == "remove":
        cmd_remove(args, project_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
