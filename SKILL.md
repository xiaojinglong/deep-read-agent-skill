---
name: read-book-skill
description: "搭建读书智能体并精读书籍：创建具名智能体、维护书单、联网核验事实、生成15000字15模块HTML深度读书笔记并自动质检。触发词：搭读书agent、创建读书智能体、帮我读书、精读一本、读3本书、书单管理。"
agent_created: true
---

# read-book-skill — 读书智能体技能

> **所有命令都由你（AI）执行。** 用户很可能完全不懂命令行，
> 不要把命令念给用户、也不要要求用户自己去输入任何命令 —— 你跑完告诉他结果就行。

## 先判断用户想要什么

用户不会照着文档说话。先按他的话定位到对应的动作：

| 用户说 | 你要做的 |
|--------|---------|
| "帮我安装这个 skill"（多半还给了链接） | 见下面「安装」 |
| "创建一个读书智能体 xxx" / "建一个叫 xxx 的读书 agent" | 走「创建具名智能体」 |
| "用 xxx 帮我读《孙子兵法》" | 先定位 xxx 的工作区，再跑精读流水线 |
| "帮我读《孙子兵法》"（没提智能体名字） | 直接用 skill 根目录跑流水线 |
| "读一本" / "再读 3 本" | 自动选书，跑 N 次流水线 |
| "书单里还有啥" / "加一本 X" / "删掉 X" | 只做书单操作，不生成笔记 |

**不要主动问用户"要把项目建在哪"**，这会造成不必要的打断。
用户给了名字就按名字建；没给名字就用 skill 根目录。

## 安装

用户常常是让你装，而不是自己装。装到当前这个 AI 工具的 skills 目录下即可：

```bash
git clone --depth 1 <仓库地址> <该工具的skills目录>/read-book-skill
```

常见位置：`~/.claude/skills/`、`~/.openclaw/skills/`、`~/.agents/skills/`。
没有 git 就下载 zip 解压过去。**不需要跑 install.py**，本 skill 零配置，复制到位即可用。

多平台批量安装才用 `python install.py`（详见 README）。

> 装完通常要**新开会话**才生效；OpenClaw 还需 `openclaw gateway restart`。

## 创建具名智能体

用户说"创建一个读书智能体 xxx"时，建一个独立工作区，名字就是 xxx：

```bash
python scripts/agent_manager.py create "<名字>" [--desc "一句话说明"]
python scripts/agent_manager.py use "<名字>"      # 拿工作区路径与书单概况
python scripts/agent_manager.py list              # 列出所有智能体
python scripts/agent_manager.py info "<名字>"
python scripts/agent_manager.py remove "<名字>"   # 只预览；--yes 才真删
```

`use` 返回 `project_dir`。**之后该智能体的所有命令都要带上它**：

```bash
python scripts/book_manager.py ensure "孙子兵法" --project-dir "<project_dir>"
```

> `--project-dir` 放在命令前或后都可以。
> 名字里不许有 `/ \ : * ? " < > |`，脚本会拒绝并提示。

每个智能体有自己的书单和笔记，建在 `agents/<名字>/` 下，互不影响。
删除前会展示待删的书单数与笔记数，必须用户确认后才能 `--yes`。

## 工作区在哪

- 用户**指定了智能体名字** → 用 `agents/<名字>/`
- 用户**没提智能体** → 用 skill 根目录（自带 `book_list.json` 与 `book_cache/`）
- 找不到 `book_list.json` → 说明装的是精简版，跑 `python scripts/init_project.py <目录>` 生成一份

## 精读流水线

**Step 0 生成 task_id** = `book_${YYYYMMDD}_${HHMM}`。

**Step 1 确定读哪本**：

```bash
# 用户点名了某本书 —— 用它。不在书单会自动加入（新智能体书单是空的，这条是必经之路）
python scripts/book_manager.py ensure "孙子兵法" --author "孙武" --priority 高

# 用户没点名 —— 自动选（高优先级 + 未读优先）
python scripts/book_manager.py select
python scripts/book_manager.py select --random
```

`ensure` 返回这本书的完整信息；`existed: false` 表示原本不在书单、已自动加入。

**Step 2 写元数据**：写入 `book_cache/book_meta/${task_id}.json`。

**Step 2.5 事实核验（强制）**：
联网检索豆瓣评分、出版信息、作者履历、写作背景、书内数据，
**以及最关键的：全书章节结构**。结果写入 `book_cache/book_meta/${task_id}_facts.md`。

铁律：没有检索到的事实就不许写，不许编章节标题、不许猜评分、不许造数据。
未核实项必须在 facts 文件里显式列出，Step 3 生成时绕开。
详见 `references/fact_check.md`。

**Step 3 生成精读内容（核心）**：
- 先用模板生成骨架：
  ```bash
  python scripts/html_template.py generate --title "书名" --author "作者" --task-id ${task_id} --tags "标签" --priority "优先级"
  ```
- 读取骨架，分 2-3 次写入完整内容至 `book_cache/book_raw_content/${task_id}.html`
- 目标：15000+ 字，15 模块，4+ 种 CSS 图表，12+ 数据行，12+ 金句，6+ 行动建议
- 详细模块结构和字数分配见 `references/pipeline.md`
- **图表硬约束**：`chart` 与 `radar` 两个容器顶部必须各写一段说明文字，
  否则质检会因"容器内文字不足 80 字"判图表无效

**Step 4 质检**：
```bash
python scripts/qc_check.py book_cache/book_raw_content/${task_id}.html
```
输出会直接列出 FAIL 项和没替换掉的占位符，照着改。不达标则补充，最多重试 2 次。

**Step 5 更新状态**：
```bash
python scripts/book_manager.py update "书名" --note-path "book_cache/book_raw_content/${task_id}.html"
```
带 `--note-path` 会把笔记路径回写到书单，之后用 `notes` 就能按书名找回笔记。
**`update` 与 `notes` 必须串行执行**，并发会让后者读到写入前的书单。

**Step 6 写日志**：写入 `book_cache/book_log/${task_id}.log`。

**Step 7 输出摘要**：告诉用户——这本书讲了什么（3 条核心洞见）、
读完能用什么（3 条行动建议）、笔记文件在哪、字数与模块统计。
若 Step 2.5 核验不完整，一并说明哪些内容未经线上核实。

## 脚本说明

所有脚本在 `scripts/` 下，都支持 `--project-dir`（默认 skill 根目录）。

### agent_manager.py — 具名智能体

```bash
create "<名字>" [--desc "说明"]   # 创建（同名会提示已存在，不覆盖）
use "<名字>"                       # 返回 project_dir 与书单概况
list / info "<名字>"               # 查看
remove "<名字>" [--yes]            # 默认只预览，--yes 才真删
```

### book_manager.py — 书单管理

```bash
ensure "书名" [--author "作者"] [--priority 高] [--tags "标签"]  # 在书单就取，不在就加
select [--title "书名"] [--random]   # 选书
update "书名" [--note-path PATH] [--all]   # 更新阅读状态（精确优先）
list [--category "分类"] [--priority 高] [--unread]
search "关键词"                       # 搜索
stats / unread                        # 统计 / 未读列表
add "书名" [--author "作者"] [--priority 高] [--tags "标签"] [--force]  # 添加（同名会拦截）
edit "书名" [--new-title "新名"] [--author "作者"] [--priority 高] [--tags "标签"] [--add-tags "标签"]
remove "书名" [--yes] [--all]         # 删除（不加 --yes 只预览）
notes [--title "书名"]                # 列出精读笔记及其路径
```

> 安全设计：`update` / `remove` / `edit` 一律**精确匹配优先**。
> 输入残缺书名若模糊命中多本会直接拒绝并列出候选，
> 避免 `remove "原则"` 连带删掉《原则生活》这类静默误伤。
> `remove` 默认只预览，必须显式 `--yes` 才真删。
> **删除是不可逆操作，必须先向用户展示待删清单并取得确认。**

### html_template.py — HTML模板生成器

```bash
generate --title "书名" --author "作者" --task-id book_20260827_1030 [--tags "标签"] [--priority "高"] [--project-dir DIR]
```

### qc_check.py — 质检脚本

```bash
qc_check.py <html_file> [<html_file> ...]
```

检查：字数≥15000、15模块有内容、≥4种有效图表、章节卡≥8、金句≥12、
数据行≥12、行动建议≥6、无占位符、HTML闭合、无重复注水。

### init_project.py — 导出独立工作区（可选）

```bash
init_project.py /path/to/new-project [--books 10]
```

只有当用户想把书单和笔记放在 skill 目录之外时才用。
具名智能体用 `agent_manager.py create` 即可，不需要它。

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

- `references/pipeline.md` — 7步流水线详解
- `references/fact_check.md` — 事实核验环节（Step 2.5 必检项、铁律、降级策略）
- `references/html_visual_standard.md` — HTML/CSS 视觉标准
- `references/quality_standard.md` — 质检标准
- `references/book_list_format.md` — 书单 JSON 格式规范

## 多本连读

用户说"读3本""连读5本"：循环执行流水线，每次选不同的书，每本生成独立 HTML，最后汇总展示。

## 约束

- 失败不中断，记录错误到日志继续执行
- 精读内容基于 AI 对书籍的理解生成，不要求原文搬运
- 章节结构、核心观点、关键数据必须忠于原书，不许虚构章节
- 涉及评分、版次、数据、章节名的断言必须有 Step 2.5 的检索依据；查不到就写"未核实"或改用定性表述
- 每次精读只读一本书
- 输出文件名：`${task_id}.html`
