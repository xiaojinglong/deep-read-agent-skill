# Changelog

本文件记录 Read Book Skill 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [5.2.0] - 2026-10-08

### Added
- 📂 **`open` 命令**：用户说"帮我打开《xxx》的读书笔记"时直接打开
  - 精确定位书 → 取最新一篇笔记 → 确认文件还在 → 用系统默认浏览器打开
  - Windows `os.startfile` / macOS `open` / Linux `xdg-open`
  - 支持 `--no-open`（只给路径）、`--index N`（同书多篇时指定）、`--latest`、省略书名（开最近一篇）
  - 四种失败都有明确回话指引：没读过 / 书不在书单 / 文件被删 / 命中多本
- 📋 `list` 输出增加 `notes` 数量、`has_note`、`note_path`、`note_exists`，
  顶层加 `with_notes` —— 用户"列出我的书单"时能一眼看出哪本有笔记
- 🧪 6 个 `open` 单元测试（含负例自测验证：故意跳过文件存在性检查时测试确实会红）

### Changed
- 📝 SKILL.md 意图表新增"加入书单 / 列出书单 / 打开笔记"三行，
  并新增「常用三件事」章节，逐条给出返回值对应的回话方式
- 📝 README 新增「装好之后，你直接说人话就行」四句话对照表

## [5.1.0] - 2026-10-08

面向「完全不懂命令行」的用户重做使用流程。

### Added
- 🤖 **具名读书智能体**（`scripts/agent_manager.py`）
  - `create` / `use` / `list` / `info` / `remove`
  - 每个智能体是 `agents/<名字>/` 下的独立工作区，有自己的书单和笔记
  - 名字会做安全校验（拒绝 `/ \ : * ? " < > |` 等）
  - `remove` 默认只预览待删内容，必须 `--yes` 才真删
- ➕ **`ensure` 命令**：用户说的书不在书单里时自动加入再读，不再报「没找到」
- 🪶 **零初始化**：`book_list.json` / `book_config.json` / `book_cache/` 缺失时自动建空的，
  且**不塞任何示例书**
- 📄 `references/fact_check.md`：Step 2.5 事实核查清单

### Changed
- 📝 SKILL.md 重写：顶部加意图映射表（"帮我安装这个 skill" / "创建一个读书智能体 xxx" /
  "用 xxx 帮我读《孙子兵法》"），命令由 AI 执行、不念给用户
- 📝 README / GETTING_STARTED 增加「完全不会命令行？看这里」三步流程，
  并把文档里的占位链接换成真实仓库地址
- 🚫 `.gitignore` 排除个人书单、笔记缓存、`agents/`、`.workbuddy/`

### Fixed
- 🐛 `--project-dir` 只能放在子命令前，放后面报 `unrecognized arguments`
  （改为 `argparse.SUPPRESS` 挂到每个子解析器，前后都行）
- 🐛 `--note-path` 相对路径按 CWD 解析，具名智能体下写出 `../../` 错路径
  （改为优先按 `project_dir` 解析）
- 🐛 `update` 重复执行会在 `notes` 里堆重复记录（改为按 `task_id`/`path` 幂等 upsert）
- 🐛 空书单时 `select` 只报「未找到匹配书籍」，AI 不知道下一步
  （改为明确提示用 `ensure` 加书）

## [Unreleased]

### Added
- 初始版本发布
- 完整的读书智能体功能
- 书单管理（添加、删除、搜索、统计）
- HTML精读笔记生成（15模块，15000+字）
- 自动质检（11项检查）
- 项目初始化脚本
- 完整的单元测试
- 详细的文档和使用指南

### Changed
- 无

### Deprecated
- 无

### Removed
- 无

### Fixed
- 无

### Security
- 无

## [5.0.0] - 2026-08-27

### Added
- 🎨 **HTML模板v5版本**
  - 暖色调精致配色系统
  - 15模块emoji标题体系
  - 场景→步骤→心法格式
  - 一页精华复盘块
  - 5种CSS可视化图表（条形图、时间线、思维导图、流程图、雷达图）
  - 响应式设计（支持移动端）

- 📚 **书单管理增强**
  - 支持10本示例书籍
  - JSON格式统一输出
  - 错误处理优化
  - 支持--project-dir参数

- ✅ **质检系统升级**
  - 11项质量检查
  - 模块内容实质检查（每模块≥200字）
  - 图表有效性检查（≥80字内容）
  - 重复注水检测
  - 支持--json格式输出

- 🧪 **测试覆盖**
  - 33个单元测试
  - 书单管理测试（16个）
  - 质检脚本测试（17个）
  - 测试运行脚本

- 📖 **文档完善**
  - 详细的README.md
  - 贡献指南（CONTRIBUTING.md）
  - 版本更新日志（CHANGELOG.md）
  - MIT许可证
  - .gitignore配置

### Changed
- 🔄 **代码优化**
  - load_books() 添加错误处理
  - to_slug() 函数实现
  - 输出格式统一为JSON
  - 模块查找逻辑优化（避免误匹配）

- 📝 **文档同步**
  - 字数限制统一为15000字
  - 模块数量统一为15个
  - 所有文档保持一致

### Fixed
- 🐛 **Bug修复**
  - 随机选书未过滤已读问题
  - qc_check.py --project-dir参数支持
  - init_project.py复制references和assets目录
  - GITIGNORE字符串未正确关闭

## [4.0.0] - 2026-08-20

### Added
- 初始版本框架
- 基础书单管理功能
- HTML模板v4版本
- 基础质检功能

### Changed
- 无

### Fixed
- 无

---

## 版本说明

### 版本号含义

- **MAJOR (主版本号)**: 不兼容的API修改
- **MINOR (次版本号)**: 向后兼容的功能性新增
- **PATCH (修订号)**: 向后兼容的问题修正

### 变更类型

- **Added**: 新功能
- **Changed**: 对现有功能的变更
- **Deprecated**: 已经不建议使用，即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: Bug修复
- **Security**: 安全相关的变更

### 链接

- GitHub Releases
- 完整变更历史

---

**感谢所有为这个项目做出贡献的人！** 🙏
