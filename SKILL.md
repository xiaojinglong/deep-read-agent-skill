---
name: read-book-skill
description: "读书智能体搭建技能。用于从零搭建一个能提供书单维护、精读一本书、生成万字深度读书笔记HTML的读书智能体。包含项目初始化、书单管理、HTML模板生成、质检脚本，以及完整的7步精读流水线（选书、元数据、生成15000字精读、质检、状态更新、日志、摘要）。当用户说搭一个读书智能体、创建读书agent、搭建精读系统、book agent、读书笔记自动生成等时触发。也可用于已有书单的精读执行：用户说读书、精读、读一本、帮我读书时，按流水线执行精读任务。"
agent_created: true
---

# read-book-skill — 读书智能体搭建技能

## 用途

在任意目录下快速搭建一个读书精读智能体，具备以下能力：

1. **书单维护** — 添加、删除、搜索、按分类/优先级列出、统计书单
2. **精读书籍** — 自动选书或指定书目，执行深度精读
3. **生成读书笔记** — 输出 15000+ 字、15 模块、5 种 CSS 图表的 HTML 精读笔记
4. **质量检查** — 自动质检字数、模块、图表、数据、金句、行动建议等

## 两种使用模式

### 模式 A — 搭建项目（从零创建）

用户说"搭一个读书智能体""创建读书agent"时：

1. 运行初始化脚本创建项目骨架：
   ```bash
   python <skill_dir>/scripts/init_project.py /path/to/new-project
   ```
   这会生成完整目录结构：`book_config.json`、`book_list.json`（含10本示例）、`scripts/`（3个核心脚本）、`references/`（参考文档）、`assets/`（模板资产）、`book_cache/`（4个子目录）、`agent_prompt/`。

2. 引导用户编辑 `book_list.json` 添加自己的书单（参考 `references/book_list_format.md`）。

3. 参考 `references/pipeline.md` 编写 `agent_prompt/main_orchestrator.md` 调度提示词。

4. 验证：`python scripts/book_manager.py stats` 查看书单统计。

### 模式 B — 执行精读（已有项目）

用户说"读书""精读""读一本""帮我读书"时，按 7 步流水线执行：

**Step 0 初始化**：确定项目根目录（book_list.json 所在目录），生成 task_id = `book_${日期}_${时段}`。

**Step 1 选书**：
```bash
python scripts/book_manager.py select                # 自动选（优先级+未读优先）
python scripts/book_manager.py select --title "书名"   # 指定书名
python scripts/book_manager.py select --random        # 随机选
```

**Step 2 写元数据**：将选中书籍信息写入 `book_cache/book_meta/${task_id}.json`。

**Step 3 生成精读内容（核心）**：
- 先用模板生成骨架：
  ```bash
  python scripts/html_template.py generate --title "书名" --author "作者" --task-id ${task_id} --tags "标签" --priority "优先级"
  ```
- 读取骨架，分 2-3 次写入完整内容至 `book_cache/book_raw_content/${task_id}.html`
- 目标：15000+ 字，15 模块，4+ 种 CSS 图表，12+ 数据行，12+ 金句，6+ 行动建议
- 详细模块结构和字数分配见 `references/pipeline.md`

**Step 4 质检**：
```bash
python scripts/qc_check.py book_cache/book_raw_content/${task_id}.html
```
质检标准详见 `references/quality_standard.md`。不达标则补充生成（最多重试2次）。

**Step 5 更新状态**：
```bash
python scripts/book_manager.py update "书名"
```

**Step 6 写日志**：将运行日志写入 `book_cache/book_log/${task_id}.log`。

**Step 7 输出摘要**：向用户展示格式化精读摘要（核心洞见3条 + 行动建议3条 + 文件路径 + 统计信息）。

## 脚本说明

所有脚本位于 `scripts/` 目录，支持 `--project-dir` 指定项目根目录（默认为脚本上级目录）。

### book_manager.py — 书单管理

```bash
select [--title "书名"] [--random]   # 选书
update "书名"                         # 更新阅读状态
list [--category "分类"] [--priority 高] [--unread]  # 列出
search "关键词"                       # 搜索
stats                                 # 统计
unread                                # 未读列表
add "书名" [--author "作者"] [--priority 高] [--tags "标签1,标签2"]  # 添加
remove "书名"                          # 删除
```

### html_template.py — HTML模板生成器

```bash
generate --title "书名" --author "作者" --task-id book_20260827_1030 [--tags "标签"] [--priority "高"] [--project-dir DIR]
```
生成 v5 暖色调精致配色 HTML 骨架，内含完整 CSS 样式（7色色板、5种图表、响应式、15模块emoji标题体系、场景步骤心法格式、一页精华复盘块）。
视觉标准详见 `references/html_visual_standard.md`。

### qc_check.py — 质检脚本

```bash
qc_check.py <html_file> [<html_file> ...]
```
检查：字数≥15000、15模块有内容、≥4种有效图表、章节卡≥8、金句≥12、数据行≥12、行动建议≥6、无占位符、HTML闭合、无重复注水。

### init_project.py — 项目初始化

```bash
init_project.py /path/to/new-project [--books 5]
```
在目标目录创建完整项目结构，复制脚本，生成配置和示例书单。

## 精读笔记 15 模块

| # | 模块 | Emoji | 字数目标 | 核心要求 |
|---|------|-------|---------|----------|
| ① | 荣誉与口碑 | 🏆 | 150 | 豆瓣评分、名人荐读、机构推荐、平台数据 |
| ② | 作者简介 | ✍️ | 600 | 身份+跨界身份+写作动机（引用块） |
| ③ | 目标读者与阅读价值 | 👥 | 700 | 4类读者画像+5项收获+实际应用价值 |
| ④ | 创作背景 | 🌐 | 600 | 时代背景+故事原型+写作手法 |
| ⑤ | **核心理论逐章拆解** | 🔬 | **5000** | **覆盖全书，每个工具含场景→步骤→心法** |
| ⑥ | 实用案例 | 📌 | 800 | 案例拆解+一句话启发 |
| ⑦ | 读者笔记精选 | 💭 | 1000 | 按主题分类，划线+批注双层 |
| ⑧ | 关键数据与事实 | 📊 | 300 | 数据+架构解读 |
| ⑨ | 金句摘录 | 💎 | 500 | 按主题分组，每条附解读 |
| ⑩ | 作者底层逻辑 | 🧠 | 700 | 因果链+可迁移法则+世界观 |
| ⑪ | 可视化图表总结 | 📈 | 700 | ≥4种CSS图表 |
| ⑫ | 落地实践指南 | 🎯 | 700 | 动作+路线图+复用场景 |
| ⑬ | 跨书关联 | 🔗 | 300 | 阅读地图+关联表格 |
| ⑭ | 客观评价 | ⚖️ | 600 | 认同+存疑+最大认知增量 |
| ⑮ | 一页精华 | 📖 | 300 | 四段式复盘+一句话总结 |

## 内容深度原则

- 每个观点都要有"为什么"：不只是作者说了什么，还有他为什么这么说
- 案例要讲细节：人物、时间、冲突、转折、结果
- 数据要有解读：数字本身不说明问题，要说清它意味着什么
- 时刻回答"所以呢"（So what）：对读者的人生有什么用
- 章节间要有联系：每章结尾说明它在全书中的位置

## 参考文档

需要更详细信息时加载对应参考文件：

- `references/pipeline.md` — 7步流水线详解（每步的输入/输出/命令/示例）
- `references/html_visual_standard.md` — HTML/CSS 视觉标准（色板、组件样式、响应式）
- `references/quality_standard.md` — 质检标准（验收清单、字数统计方法、常见问题）
- `references/book_list_format.md` — 书单 JSON 格式规范（字段说明、管理命令）

## 模板资产

- `assets/book_config.json` — 配置文件模板（HTML样式、模块、质检标准、选书规则）
- `assets/book_list_template.json` — 书单模板（10本示例书籍）

## 多本连读

用户可说"读3本""连读5本"：循环执行 Step 0-7，每次选不同的书，每本生成独立 HTML，最后汇总展示。

## 约束

- 失败不中断，记录错误到日志继续执行
- 精读内容基于 AI 对书籍的理解生成，不要求原文搬运
- 章节结构、核心观点、关键数据必须忠于原书，不许虚构章节
- 每次精读只读一本书
- 输出文件名：`${task_id}.html`
