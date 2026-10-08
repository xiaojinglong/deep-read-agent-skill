# 📚 Read Book Skill - 读书智能体

> 一个能自动精读书籍、生成15000+字深度读书笔记的AI智能体技能

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-5.0-orange.svg)]()
[![Tests](https://img.shields.io/badge/Tests-33%20passed-brightgreen.svg)]()

---

## 完全不会命令行？看这里

你只需要做两件事，**剩下的都由 AI 去做**。

**第 1 步**：把下面这句话发给你的 AI 工具（OpenClaw、Claude、Cursor 等都行）：

> 帮我安装这个 skill：https://github.com/xiaojinglong/deep-read-agent-skill

（如果你拿到的是别人给你的另一个链接，把链接换掉即可，话不用改。）

**第 2 步**：装好后（可能需要新开一个对话），继续说：

> 帮我创建一个读书智能体，名字叫「我的书房」

**第 3 步**：开始读书：

> 用「我的书房」帮我精读《孙子兵法》

就这么简单。**你不需要碰任何命令、任何文件、任何目录。**
创建出来的智能体有自己的书单和笔记，笔记是 HTML 文件，可以直接发给别人看。

<details>
<summary>给 AI 看的安装说明（如果你是 AI，请读这段）</summary>

把这个仓库放到当前 AI 工具的 skills 目录下即可，**不需要执行 install.py**：

```bash
git clone --depth 1 https://github.com/xiaojinglong/deep-read-agent-skill.git ~/.openclaw/skills/read-book-skill
# 其他常见位置：~/.claude/skills/  ~/.agents/skills/  ~/.cursor/skills/
```

没有 git 就下载 zip 解压过去。本 skill 零配置，复制到位即用。
装完提醒用户新开会话（OpenClaw 还需 `openclaw gateway restart`）。

用户说「创建一个读书智能体 xxx」时执行：
```bash
python scripts/agent_manager.py create "xxx"
python scripts/agent_manager.py use "xxx"     # 拿到 project_dir
```
后续该智能体的命令都加 `--project-dir "<project_dir>"`（位置前后都行）。
用户点名要读的书若不在书单，用 `book_manager.py ensure "书名"` 自动加入。

完整行为指南见 `SKILL.md`。
</details>

---

## 🎯 这是什么？

Read Book Skill 是一个**AI驱动的读书智能体**，它可以：

- 📖 **自动精读书籍** - 基于书籍内容生成深度分析
- 📝 **生成万字笔记** - 15000+字、15模块的HTML精读笔记
- 🎨 **精美排版输出** - 暖色调CSS设计，5种可视化图表
- ✅ **自动质量检查** - 11项质检确保内容质量

**适合谁用？**
- 📚 爱读书但没时间做笔记的人
- 🎓 需要深度理解书籍的学生和研究者
- 💼 需要快速掌握商业书籍的职场人
- 🤖 想要构建读书AI助手的开发者

## 📸 效果展示

### 生成的精读笔记

![精读笔记示例](examples/screenshot.png)

### 核心功能

| 功能 | 说明 | 示例 |
|------|------|------|
| 智能选书 | 按优先级、分类自动选书 | `python scripts/book_manager.py select` |
| 深度精读 | 15000+字、15模块笔记 | `python scripts/html_template.py generate` |
| 自动质检 | 11项质量检查 | `python scripts/qc_check.py file.html` |
| 书单管理 | 添加、搜索、统计 | `python scripts/book_manager.py stats` |

## ✨ 功能特性

- 📖 **智能选书** - 按优先级、分类、阅读状态自动选书
- 📝 **深度精读** - 自动生成15000+字、15模块的HTML精读笔记
- 🎨 **精美排版** - 暖色调CSS设计，5种可视化图表
- ✅ **自动质检** - 字数、模块、图表、金句等11项质量检查
- 📊 **书单管理** - 添加、删除、搜索、统计书单
- 🔄 **批量阅读** - 支持多本连读，自动生成摘要

## 📦 安装到任意 AI 工具

本项目遵循 **Agent Skills 开放标准**（Anthropic 发起，Claude Code / Codex / Cursor /
Copilot / Gemini CLI / OpenClaw / WorkBuddy 等均已支持）。一份 SKILL.md，装到哪都能用。

### 方式一：一键安装（推荐）

```bash
python install.py
```

脚本会自动探测本机装了哪些 AI 工具，把 skill 分发到各自目录：

| 目标 | 路径 | 工具 |
|------|------|------|
| `agents` | `~/.agents/skills/` | **通用总线**，Cursor/Copilot/Gemini/Zed/OpenCode 等多数工具都读 |
| `claude` | `~/.claude/skills/` | Claude Code |
| `openclaw` | `~/.openclaw/skills/` | OpenClaw |
| `workbuddy` | `~/.workbuddy/skills/` | WorkBuddy |
| `codex` | `~/.codex/skills/` | Codex CLI |
| `gemini` | `~/.gemini/skills/` | Gemini CLI |
| `cursor` | `~/.cursor/skills/` | Cursor |
| `opencode` | `~/.config/opencode/skills/` | OpenCode |

常用参数：

```bash
python install.py --list                      # 只看能装到哪，不安装
python install.py --targets claude,openclaw   # 只装指定工具
python install.py --force                     # 连书单和笔记一起覆盖（默认会保留）
```

安装器只会分发必要文件（`SKILL.md` / `scripts` / `references` / `assets` / 数据区），
不会把 `tests`、`examples`、`.git` 之类的东西带过去。
**升级时默认保留你的书单和笔记**，不会冲掉数据。

### 方式二：手动安装

把下面这些放进你的 AI 工具的 skills 目录即可（每个工具一个子目录，名字随意）：

```
read-book-skill/
├── SKILL.md          # 必需
├── scripts/          # 必需
├── references/       # 推荐
├── assets/           # 推荐
├── book_list.json    # 书单（可选，缺失时按 init 生成）
└── book_cache/       # 笔记存放处
```

### 装完之后

**新开一个会话**让工具刷新 skill 列表，然后直接说：

> 帮我读一本《穷查理宝典》

不需要初始化、不需要选目录——skill 目录本身就是工作区，书单和笔记都存在这里。

### 关于 `{baseDir}`

有些 skill 用 `{baseDir}` 引用自身目录。那是 **Claude Code 的私有语法，不在开放标准里**，
换到 Cursor / Gemini 等工具会解析失败。本项目一律用**相对路径**，
兼容性最好（这也是 anthropics 官方 skill 仓库的做法）。

## 🚀 快速开始

### 一键开始（推荐）

**Windows用户**：
```bash
# 双击运行
examples\quick_start.bat
```

**Mac/Linux用户**：
```bash
# 运行脚本
bash examples/quick_start.sh
```

### 手动开始

#### 1. 克隆项目

```bash
git clone --depth 1 https://github.com/xiaojinglong/deep-read-agent-skill.git read-book-skill
cd read-book-skill
```

#### 2. 初始化读书项目

```bash
python scripts/init_project.py /path/to/your-book-project
```

这会创建完整的项目结构：
```
your-book-project/
├── book_config.json          # 配置文件
├── book_list.json            # 书单数据（含10本示例）
├── scripts/                  # 核心脚本
├── references/               # 参考文档
├── assets/                   # 模板资产
├── agent_prompt/             # Agent提示词
└── book_cache/               # 缓存目录
    ├── book_meta/            # 书籍元数据
    ├── book_raw_content/     # 精读笔记HTML
    ├── push_result/          # 推送结果
    └── book_log/             # 运行日志
```

### 3. 管理书单

```bash
# 查看书单统计
python scripts/book_manager.py stats

# 添加新书（同名会被拦截）
python scripts/book_manager.py add "书名" --author "作者" --priority 高 --tags "标签1,标签2"

# 修改书籍信息
python scripts/book_manager.py edit "书名" --new-title "新书名" --author "作者" \
  --priority 高 --tags "标签" --add-tags "追加标签"

# 删除（默认只预览，确认后加 --yes）
python scripts/book_manager.py remove "书名"
python scripts/book_manager.py remove "书名" --yes

# 查看精读笔记
python scripts/book_manager.py notes --title "书名"

# 列出所有书
python scripts/book_manager.py list

# 搜索书籍
python scripts/book_manager.py search "关键词"
```

### 4. 执行精读

```bash
# 自动选书（按优先级）
python scripts/book_manager.py select

# 指定书名选书
python scripts/book_manager.py select --title "书名"

# 生成HTML骨架
python scripts/html_template.py generate --title "书名" --author "作者" --task-id book_20260827_1030

# 填充内容（AI生成15000+字精读笔记）

# 质检
python scripts/qc_check.py book_cache/book_raw_content/book_20260827_1030.html

# 更新阅读状态（可同时回写笔记路径）
python scripts/book_manager.py update "书名" \
  --note-path "book_cache/book_raw_content/xxx.html"
```

> `update` / `edit` / `remove` 均为**精确匹配优先**：残缺书名若模糊命中多本会直接拒绝并列出候选，
> 避免误导伤到《原则生活》这类相近书名。`remove` 不加 `--yes` 只预览不删除。

## 🎯 使用场景

### 场景1：快速掌握商业书籍
```bash
# 你：帮我读一本《原则》
# AI：自动生成15000+字精读笔记，包含核心理论、案例、行动建议
```

### 场景2：批量阅读书单
```bash
# 你：帮我读3本书
# AI：自动循环执行精读流程，每本书生成独立笔记
```

### 场景3：建立个人知识库
```bash
# 添加书籍到书单
python scripts/book_manager.py add "书名" --author "作者" --priority 高

# 定期精读
python scripts/book_manager.py select

# 查看阅读统计
python scripts/book_manager.py stats
```

## ⚡ 性能说明

| 指标 | 数值 | 说明 |
|------|------|------|
| 生成时间 | 2-5分钟 | 取决于AI响应速度 |
| 笔记字数 | 15000+字 | 每份精读笔记 |
| 模块数量 | 15个 | 完整的知识结构 |
| 图表数量 | 5种 | 可视化展示 |
| 质检项目 | 11项 | 全面质量检查 |
| 支持格式 | HTML | 精美排版，支持移动端 |

**系统要求**：
- Python 3.7+
- 仅使用标准库，无需额外依赖
- 支持 Windows、macOS、Linux

## ⚠️ 局限性说明

1. **内容生成依赖AI** - 精读笔记内容由AI生成，可能需要人工校对
2. **专业书籍效果有限** - 对于高度专业的技术书籍，可能需要补充领域知识
3. **中文书籍优化** - 目前主要针对中文书籍优化，英文书籍支持有限
4. **单次处理** - 每次只能精读一本书，不支持并行处理

## 📁 项目结构

```
read-book-skill/
├── SKILL.md                    # 技能说明文档（Claude Code使用）
├── README.md                   # 本文件
├── LICENSE                     # MIT许可证
├── requirements.txt            # Python依赖
├── .gitignore                  # Git忽略规则
├── run_tests.py                # 测试运行脚本
│
├── scripts/                    # 核心脚本
│   ├── book_manager.py         # 书单管理（增删改查、选书、笔记索引）
│   ├── html_template.py        # HTML模板生成器（v5版本，15模块）
│   ├── qc_check.py             # 质检脚本（11项检查）
│   └── init_project.py         # 项目初始化脚本
│
├── tests/                      # 单元测试
│   ├── test_book_manager.py    # 书单管理测试
│   └── test_qc_check.py        # 质检脚本测试
│
├── references/                 # 参考文档
│   ├── pipeline.md             # 7步流水线详解
│   ├── quality_standard.md     # 质检标准
│   ├── html_visual_standard.md # HTML视觉标准
│   └── book_list_format.md     # 书单JSON格式规范
│
└── assets/                     # 模板资产
    ├── book_config.json        # 配置文件模板
    └── book_list_template.json # 书单模板（10本示例）
```

## 📖 精读笔记模块

一份完整的精读笔记包含15个模块：

| # | 模块 | Emoji | 字数目标 | 核心要求 |
|---|------|-------|---------|----------|
| ① | 荣誉与口碑 | 🏆 | 150 | 豆瓣评分、名人荐读、机构推荐 |
| ② | 作者简介 | ✍️ | 600 | 身份+跨界身份+写作动机 |
| ③ | 目标读者与阅读价值 | 👥 | 700 | 4类读者画像+5项收获 |
| ④ | 创作背景 | 🌐 | 600 | 时代背景+故事原型+写作手法 |
| ⑤ | **核心理论逐章拆解** | 🔬 | **5000** | **覆盖全书，场景→步骤→心法** |
| ⑥ | 实用案例 | 📌 | 800 | 案例拆解+一句话启发 |
| ⑦ | 读者笔记精选 | 💭 | 1000 | 按主题分类，划线+批注 |
| ⑧ | 关键数据与事实 | 📊 | 300 | 数据+架构解读 |
| ⑨ | 金句摘录 | 💎 | 500 | 按主题分组，每条附解读 |
| ⑩ | 作者底层逻辑 | 🧠 | 700 | 因果链+可迁移法则+世界观 |
| ⑪ | 可视化图表总结 | 📈 | 700 | ≥4种CSS图表 |
| ⑫ | 落地实践指南 | 🎯 | 700 | ≥6条行动建议+路线图 |
| ⑬ | 跨书关联 | 🔗 | 300 | 阅读地图+关联表格 |
| ⑭ | 客观评价 | ⚖️ | 600 | 认同+存疑+最大认知增量 |
| ⑮ | 一页精华 | 📖 | 300 | 四段式复盘+一句话总结 |

## 🔧 配置说明

### book_config.json

```json
{
  "version": "5.0",
  "min_words": 15000,
  "target_words": 15000,
  "max_regenerate": 2,
  "html_style": {
    "background": "#faf9f6",
    "font_size": "18px",
    "line_height": "1.85",
    "max_width": "820px"
  },
  "modules": ["荣誉与口碑", "作者简介", ...],
  "quality_check": {
    "min_words": 15000,
    "module_count": 15,
    "min_charts": 4,
    "min_quotes": 12
  }
}
```

### 自定义字数限制

如需修改字数限制，需要同步修改以下文件：

1. `scripts/qc_check.py` - 质检阈值
2. `scripts/init_project.py` - 配置模板
3. `scripts/html_template.py` - 提示文案
4. `SKILL.md` - 文档说明
5. `references/pipeline.md` - 流水线文档
6. `references/quality_standard.md` - 质检标准

## 🧪 运行测试

```bash
# 运行所有测试
python run_tests.py

# 详细输出
python run_tests.py -v

# 运行特定测试
python run_tests.py TestBookManager
```

## 📋 质检标准

精读笔记必须通过以下全部检查：

| 检查项 | 阈值 | 说明 |
|--------|------|------|
| 正文字数 | ≥ 15000 | 去除CSS后的纯文字 |
| 模块完整 | 15/15 | 15个模块全部存在 |
| 模块有内容 | 15/15 | 每模块≥200字实质内容 |
| 图表种类 | ≥ 4种 | 5种图表中至少4种 |
| 章节卡片 | ≥ 8 | chapter-card数量 |
| 金句 | ≥ 12 | blockquote数量 |
| 数据表行 | ≥ 12 | tr数量 |
| 行动建议 | ≥ 6 | 落地实践指南中的li |
| 占位符 | 0 | 无【...】、TODO残留 |
| HTML闭合 | 是 | 以</html>结尾 |
| 无重复注水 | 是 | 长句不重复3次以上 |

## 🔄 更新说明

### 如何获取最新版本？

```bash
# 克隆最新版本
git clone --depth 1 https://github.com/xiaojinglong/deep-read-agent-skill.git read-book-skill

# 或者拉取更新
cd read-book-skill
git pull origin master
```

> 仓库默认分支是 `master`。

### 如何贡献代码？

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 贡献方式

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范

- Python代码遵循PEP8规范
- 添加新功能需要编写单元测试
- 修改文档需要同步更新README.md
- 提交前运行测试确保通过

## ❓ 常见问题

**Q: 需要安装什么依赖？**
A: 仅需Python 3.7+，使用标准库，无需额外安装。

**Q: 生成一份笔记需要多长时间？**
A: 通常2-5分钟，取决于AI响应速度。

**Q: 支持哪些书籍？**
A: 理论上支持所有书籍，但中文商业、社科类书籍效果最佳。

**Q: 如何自定义字数限制？**
A: 修改`book_config.json`中的`min_words`和`target_words`字段。

更多问题详见 [FAQ.md](FAQ.md)

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 感谢所有贡献者和使用者
- 特别感谢刘润老师的《底层逻辑》启发
- 灵感来源于对深度阅读的热爱

## 📧 联系方式

- Issues: GitHub Issues
- Discussions: GitHub Discussions

## ⭐ Star History

如果这个项目对你有帮助，请给个Star支持一下！

---

**读书使人充实，思考使人深邃，交流使人清醒。** - 弗朗西斯·培根
