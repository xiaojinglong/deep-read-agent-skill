# 🚀 快速开始指南

本指南帮助你在5分钟内开始使用 Read Book Skill。

## 📋 前置条件

- Python 3.7 或更高版本
- 基本的命令行操作知识
- 一个文本编辑器（可选）

## 🎯 方式一：快速体验（推荐新手）

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/read-book-skill.git
cd read-book-skill
```

### 2. 初始化项目

```bash
python scripts/init_project.py ./my-first-book-project
```

### 3. 查看书单

```bash
cd my-first-book-project
python scripts/book_manager.py stats
```

你会看到类似输出：
```json
{
  "total": 10,
  "read": 0,
  "unread": 10,
  "read_percentage": "0%",
  "priority_distribution": {"高": 5, "中": 5},
  "top_tags": {"投资": 3, "思维模型": 2, "心理学": 2}
}
```

### 4. 选一本书

```bash
python scripts/book_manager.py select
```

输出示例：
```json
{
  "selected": true,
  "title": "穷查理宝典",
  "author": "查理·芒格",
  "priority": "高",
  "tags": ["投资", "思维模型"],
  "last_read": null,
  "en_slug": "qiong-cha-li-bao-dian"
}
```

### 5. 生成精读笔记骨架

```bash
python scripts/html_template.py generate \
  --title "穷查理宝典" \
  --author "查理·芒格" \
  --task-id book_20260827_1000 \
  --tags "投资,思维模型" \
  --priority "高"
```

### 6. 查看生成的文件

```bash
ls book_cache/book_raw_content/
# 输出: book_20260827_1000.html
```

用浏览器打开这个HTML文件，你会看到精读笔记的骨架模板。

## 🎯 方式二：完整精读流程

### 1. 准备工作

```bash
cd my-first-book-project
```

### 2. 添加你想读的书

```bash
python scripts/book_manager.py add "你的书名" \
  --author "作者名" \
  --priority 高 \
  --tags "标签1,标签2"
```

### 3. 选书

```bash
# 指定书名选书
python scripts/book_manager.py select --title "你的书名"

# 或者自动选书（按优先级）
python scripts/book_manager.py select
```

### 4. 生成精读笔记

这一步需要AI（如Claude）来填充内容：

1. **生成骨架**：
   ```bash
   python scripts/html_template.py generate \
     --title "你的书名" \
     --author "作者名" \
     --task-id book_20260827_1200
   ```

2. **AI填充内容**：
   - 读取骨架文件
   - 按15个模块填充内容
   - 目标15000+字
   - 分2-3次写入

3. **质检**：
   ```bash
   python scripts/qc_check.py book_cache/book_raw_content/book_20260827_1200.html
   ```

4. **更新状态**：
   ```bash
   python scripts/book_manager.py update "你的书名"
   ```

### 5. 查看结果

用浏览器打开生成的HTML文件，享受你的精读笔记！

## 🎯 方式三：使用Claude Code自动化

如果你使用Claude Code，可以直接说：

```
帮我读一本《底层逻辑》
```

Claude Code会自动执行完整的7步流水线：
1. 初始化项目
2. 添加书籍到书单
3. 选书
4. 生成精读笔记
5. 质检
6. 更新状态
7. 输出摘要

## 📚 常见操作

### 书单管理

```bash
# 查看所有书
python scripts/book_manager.py list

# 按优先级筛选
python scripts/book_manager.py list --priority 高

# 只看未读
python scripts/book_manager.py list --unread

# 搜索书籍
python scripts/book_manager.py search "关键词"

# 删除书籍
python scripts/book_manager.py remove "书名"
```

### 质检操作

```bash
# 检查单个文件
python scripts/qc_check.py book_cache/book_raw_content/book_20260827_1200.html

# 检查所有文件
python scripts/qc_check.py book_cache/book_raw_content/*.html

# JSON格式输出
python scripts/qc_check.py --json book_cache/book_raw_content/*.html
```

### 批量阅读

```bash
# 读3本书
# Claude Code会自动循环执行Step 0-7
帮我读3本书
```

## 🔧 自定义配置

### 修改字数限制

编辑 `book_config.json`：

```json
{
  "min_words": 15000,
  "target_words": 15000
}
```

### 修改选书规则

编辑 `book_config.json`：

```json
{
  "selection_rules": {
    "priority_order": ["高", "中", "低"],
    "prefer_unread": true,
    "prefer_null_last_read": true
  }
}
```

### 修改HTML样式

编辑 `book_config.json` 中的 `html_style` 部分：

```json
{
  "html_style": {
    "background": "#faf9f6",
    "font_size": "18px",
    "line_height": "1.85",
    "max_width": "820px"
  }
}
```

## ❓ 常见问题

### Q: 质检失败怎么办？

A: 查看FAIL项，针对性补充：
- 字数不足：补充更多内容
- 模块缺失：检查15个模块是否都有内容
- 图表不足：添加CSS图表
- 金句不足：添加blockquote
- 行动建议不足：在落地实践指南中添加li

### Q: 如何批量导入书单？

A: 编辑 `book_list.json`，按格式添加：

```json
[
  {
    "title": "书名",
    "author": "作者",
    "priority": "高",
    "tags": ["标签1", "标签2"],
    "en_slug": "english-slug",
    "user_read": false,
    "last_read": null
  }
]
```

### Q: 如何导出精读笔记？

A: 直接复制 `book_cache/book_raw_content/` 目录下的HTML文件，它们是独立的、可分享的。

### Q: 支持哪些书籍？

A: 理论上支持所有书籍。AI会根据书籍内容生成精读笔记。对于专业性强的书籍，可能需要人工补充。

## 🎓 进阶使用

### 1. 自定义Agent提示词

编辑 `agent_prompt/main_orchestrator.md`，定义你的精读流程。

### 2. 集成到工作流

使用Claude Code的skill功能，将读书智能体集成到你的日常工作流。

### 3. 扩展功能

- 添加新的质检规则
- 自定义HTML模板样式
- 集成推送功能（邮件、笔记软件等）

## 📖 示例项目

查看 `my-book-project/` 目录，这是一个完整的示例项目，包含：
- 10本示例书籍
- 一份完整的精读笔记示例
- 完整的日志和元数据

## 🆘 获取帮助

- 📖 查看 [README.md](README.md)
- 🐛 报告问题：GitHub Issues
- 💬 讨论交流：GitHub Discussions
- 📧 联系作者：请通过GitHub联系

## 🎉 开始使用

现在你已经了解了基本用法，开始你的精读之旅吧！

```bash
cd my-first-book-project
python scripts/book_manager.py select
```

**祝你阅读愉快！** 📚✨
