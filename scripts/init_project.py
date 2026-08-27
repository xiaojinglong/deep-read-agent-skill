#!/usr/bin/env python3
"""读书智能体 - 项目初始化脚本

在指定目录下初始化一个完整的读书智能体项目结构。

Usage:
  python init_project.py /path/to/my-book-project
  python init_project.py /path/to/my-book-project --books 20

生成的目录结构:
  my-book-project/
  ├── book_config.json          # 配置文件
  ├── book_list.json           # 书单数据（空模板）
  ├── scripts/                 # 脚本目录（符号链接或复制）
  ├── agent_prompt/            # Agent 提示词目录
  ├── book_cache/
  │   ├── book_meta/           # 书籍元数据
  │   ├── book_raw_content/    # 精读笔记HTML输出
  │   ├── push_result/         # 推送结果
  │   └── book_log/            # 运行日志
  └── .gitignore
"""

import json
import os
import sys
import argparse
import shutil
from pathlib import Path


CONFIG_TEMPLATE = {
    "version": "5.0",
    "book_list_path": "book_list.json",
    "output_dirs": {
        "book_meta": "book_cache/book_meta",
        "book_raw_content": "book_cache/book_raw_content",
        "push_result": "book_cache/push_result",
        "book_log": "book_cache/book_log"
    },
    "min_words": 15000,
    "target_words": 15000,
    "max_regenerate": 2,
    "html_style": {
        "background": "#faf9f6",
        "card_background": "#ffffff",
        "font_size": "18px",
        "line_height": "1.85",
        "max_width": "820px",
        "title_size": "23px",
        "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif",
        "shadow_sm": "0 1px 3px rgba(0,0,0,0.06)",
        "shadow_md": "0 4px 12px rgba(0,0,0,0.08)",
        "shadow_lg": "0 8px 24px rgba(0,0,0,0.10)"
    },
    "modules": [
        "荣誉与口碑", "作者简介", "目标读者与阅读价值", "创作背景",
        "核心理论逐章拆解", "实用案例", "读者笔记精选", "关键数据与事实",
        "金句摘录", "作者底层逻辑", "可视化图表总结", "落地实践指南",
        "跨书关联", "客观评价", "一页精华"
    ],
    "quality_check": {
        "min_words": 15000,
        "module_count": 15,
        "min_charts": 4,
        "min_data_rows": 12,
        "min_quotes": 12,
        "min_actions": 6,
        "chapter_coverage": "all"
    },
    "selection_rules": {
        "priority_order": ["高", "中", "低"],
        "prefer_unread": True,
        "prefer_null_last_read": True
    }
}

BOOK_LIST_TEMPLATE = [
    {
        "title": "穷查理宝典",
        "author": "查理·芒格",
        "priority": "高",
        "tags": ["投资", "思维模型"],
        "en_slug": "qiong-cha-li-bao-dian",
        "user_read": False,
        "last_read": None
    },
    {
        "title": "思考，快与慢",
        "author": "丹尼尔·卡尼曼",
        "priority": "高",
        "tags": ["心理学", "决策"],
        "en_slug": "si-kao-kuai-yu-man",
        "user_read": False,
        "last_read": None
    },
    {
        "title": "系统之美",
        "author": "德内拉·梅多斯",
        "priority": "高",
        "tags": ["系统思维"],
        "en_slug": "xi-tong-zhi-mei",
        "user_read": False,
        "last_read": None
    },
    {
        "title": "反脆弱",
        "author": "纳西姆·塔勒布",
        "priority": "高",
        "tags": ["风险", "哲学"],
        "en_slug": "fan-cui-ruo",
        "user_read": False,
        "last_read": None
    },
    {
        "title": "人类简史",
        "author": "尤瓦尔·赫拉利",
        "priority": "高",
        "tags": ["历史", "人类文明史"],
        "en_slug": "ren-lei-jian-shi",
        "user_read": False,
        "last_read": None
    },
    {
        "title": "原则",
        "author": "瑞·达利欧",
        "priority": "高",
        "tags": ["管理", "投资", "人生哲学"],
        "en_slug": "yuan-ze",
        "user_read": False,
        "last_read": None
    },
    {
        "title": "高效能人士的七个习惯",
        "author": "史蒂芬·柯维",
        "priority": "中",
        "tags": ["自我管理", "领导力"],
        "en_slug": "gao-xiao-neng-xi-guan",
        "user_read": False,
        "last_read": None
    },
    {
        "title": "刻意练习",
        "author": "安德斯·艾利克森",
        "priority": "中",
        "tags": ["学习方法", "技能提升"],
        "en_slug": "ke-yi-lian-xi",
        "user_read": False,
        "last_read": None
    },
    {
        "title": "黑天鹅",
        "author": "纳西姆·塔勒布",
        "priority": "中",
        "tags": ["风险", "不确定性", "哲学"],
        "en_slug": "hei-tian-e",
        "user_read": False,
        "last_read": None
    },
    {
        "title": "认知觉醒",
        "author": "周岭",
        "priority": "中",
        "tags": ["认知科学", "自我成长"],
        "en_slug": "ren-zhi-jue-xing",
        "user_read": False,
        "last_read": None
    }
]

GITIGNORE = """book_cache/book_log/
book_cache/push_result/
__pycache__/
*.pyc
.DS_Store
.idea/
.vscode/
*.swp
*~
"""


def init_project(target_dir: str, num_books: int = 5):
    project = Path(target_dir).resolve()
    project.mkdir(parents=True, exist_ok=True)

    # 创建子目录
    dirs = [
        "scripts", "agent_prompt", "references", "assets",
        "book_cache/book_meta",
        "book_cache/book_raw_content",
        "book_cache/push_result",
        "book_cache/book_log",
    ]
    for d in dirs:
        (project / d).mkdir(parents=True, exist_ok=True)

    # 写配置文件
    config_path = project / "book_config.json"
    config_path.write_text(
        json.dumps(CONFIG_TEMPLATE, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # 写书单模板
    book_list_path = project / "book_list.json"
    books = BOOK_LIST_TEMPLATE[:num_books] if num_books <= len(BOOK_LIST_TEMPLATE) else BOOK_LIST_TEMPLATE
    book_list_path.write_text(
        json.dumps(books, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # 写 .gitignore
    (project / ".gitignore").write_text(GITIGNORE, encoding="utf-8")

    # 复制脚本文件
    skill_root = Path(__file__).resolve().parent.parent  # skill根目录
    skill_scripts = skill_root / "scripts"
    scripts_to_copy = ["book_manager.py", "html_template.py", "qc_check.py"]
    for script_name in scripts_to_copy:
        src = skill_scripts / script_name
        dst = project / "scripts" / script_name
        if src.exists():
            shutil.copy2(src, dst)

    # 复制references目录
    skill_references = skill_root / "references"
    if skill_references.exists():
        for ref_file in skill_references.glob("*.md"):
            shutil.copy2(ref_file, project / "references" / ref_file.name)

    # 复制assets目录
    skill_assets = skill_root / "assets"
    if skill_assets.exists():
        for asset_file in skill_assets.glob("*"):
            if asset_file.is_file():
                shutil.copy2(asset_file, project / "assets" / asset_file.name)

    # 写一个空的 agent_prompt 占位文件
    orchestrator_path = project / "agent_prompt" / "main_orchestrator.md"
    orchestrator_path.write_text(
        "# 读书精读智能体 - 主调度提示词\n\n"
        "> 参考 references/pipeline.md 编写完整流水线提示词\n",
        encoding="utf-8"
    )

    print(f"[OK] 项目已初始化: {project}")
    print(f"  书单: {book_list_path} ({len(books)} 本)")
    print(f"  配置: {config_path}")
    print(f"  脚本: {project / 'scripts'}")
    print(f"  参考文档: {project / 'references'}")
    print(f"  模板资产: {project / 'assets'}")
    print(f"\n下一步:")
    print(f"  1. 编辑 book_list.json 添加你的书单（参考 references/book_list_format.md）")
    print(f"  2. 参考 references/pipeline.md 编写 agent_prompt/main_orchestrator.md")
    print(f"  3. 运行: python scripts/book_manager.py stats 查看书单统计")
    print(f"  4. 运行: python scripts/book_manager.py select 选书")


def main():
    parser = argparse.ArgumentParser(description="初始化读书智能体项目")
    parser.add_argument("target_dir", help="项目目标目录")
    parser.add_argument("--books", type=int, default=5, help="模板书单数量（默认5）")
    args = parser.parse_args()
    init_project(args.target_dir, args.books)


if __name__ == "__main__":
    main()
