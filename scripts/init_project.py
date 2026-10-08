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


ORCHESTRATOR_TEMPLATE = """# 读书精读智能体 — 主调度提示词

> 目标：一次精读产出一份 >=15000 字、15 模块、含 4+ 种图表的 HTML 精读笔记。

## 执行前

- 项目根目录 = 本文件所在目录的上一级（含 `book_list.json`）
- `task_id` = `book_${YYYYMMDD}_${HHMM}`
- 所有脚本用 `python` 执行，路径相对项目根目录

## 流水线

### Step 1 选书

```bash
python scripts/book_manager.py select                 # 自动（优先级+未读优先）
python scripts/book_manager.py select --title "书名"   # 指定
```

输出 JSON 拿到 `title` / `author` / `tags` / `priority`。

### Step 2 写元数据

写入 `book_cache/book_meta/${task_id}.json`。

### Step 2.5 事实核验（强制，不可跳过）

这一步决定笔记的可信度。规范见 `references/fact_check.md`。

用搜索工具跑完以下必检项：

| 必检项 | 检索词模板 |
|--------|-----------|
| 豆瓣评分 | `<书名> 豆瓣 评分` |
| 出版信息 | `<书名> <作者> 出版社 版次` |
| 作者履历 | `<作者> 身份 履历 代表作` |
| **全书章节结构** | `<书名> 目录 章节 大纲` |
| 写作背景 | `<书名> 创作背景 为什么写这本书` |
| 书内数据 | `<书名> 数据 统计 研究发现` |

结果写入 `book_cache/book_meta/${task_id}_facts.md`，未核实项必须显式列出。

**铁律**：查不到就不许写 —— 不编章节标题、不猜评分、不造数据。
模块⑤ 占 5000 字，章节名一旦虚构整篇报废。
检索全部失败则降级：改定性表述 + 按论证脉络组织 + 结尾说明未核验。

### Step 3 生成内容

**3.1 生成骨架**

```bash
python scripts/html_template.py generate \\
  --title "书名" --author "作者" \\
  --task-id ${task_id} --tags "标签" --priority "高"
```

**3.2 分 2-3 次填充**

读取骨架，按 15 模块分批写入 `book_cache/book_raw_content/${task_id}.html`。
字数合计 >=15000（模块⑤ 核心理论逐章拆解约 5000 字，需 >=8 个 chapter-card）。

所有数字、评分、章节名必须来自 Step 2.5 的事实清单。
模型记忆只能用于观点阐述，不能用于事实断言。

**3.3 图表**
至少 4 种 CSS 图表，且必须替换掉骨架示例里的【...】占位内容，换成本书真实数据。
可用图表容器：chart / timeline / mindmap / flow / radar

### Step 4 质检

```bash
python scripts/qc_check.py book_cache/book_raw_content/${task_id}.html
```

输出会列出未替换占位符的具体条目，照着改即可。不达标则针对性补充，最多重试 2 次。

### Step 5 更新状态

```bash
python scripts/book_manager.py update "书名" \\
  --note-path "book_cache/book_raw_content/${task_id}.html"
```

务必带 `--note-path`：笔记路径会回写进书单，之后用 `notes` 命令能按书名找回。
书名要与 `select` 返回的完全一致，以便精确匹配。

### Step 6 写日志

写入 `book_cache/book_log/${task_id}.log`。

### Step 7 输出摘要

向用户输出：本书概况 -> 核心洞见 3 条 -> 行动建议 3 条 -> 文件路径 -> 统计信息
（字数 / 模块数 / 图表数）。若 Step 2.5 核验不完整，一并说明哪些内容未经线上核实。

## 用户常见的书单操作

```bash
python scripts/book_manager.py list [--unread] [--priority 高]
python scripts/book_manager.py search "关键词"
python scripts/book_manager.py stats
python scripts/book_manager.py add "书名" --author "作者" --priority 高 --tags "标签"
python scripts/book_manager.py edit "书名" --priority 中 --add-tags "标签"
python scripts/book_manager.py remove "书名" --yes
python scripts/book_manager.py notes --title "书名"
```

安全约定：`update` / `edit` / `remove` 一律精确优先，残缺书名若模糊命中多本会拒绝
并列出候选；`remove` 不加 `--yes` 只做预览。

## 约束

- 失败不中断，记录错误继续
- 每次精读只读一本书
- 输出文件名 `${task_id}.html`
- **宁可写"未核实"，不可编事实**
- **删除书单条目属于不可逆操作，必须先展示待删清单并得到用户确认**
"""

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
    orchestrator_path.write_text(ORCHESTRATOR_TEMPLATE, encoding="utf-8")

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
