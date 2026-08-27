# ❓ 常见问题解答 (FAQ)

## 目录

- [基础问题](#基础问题)
- [安装和配置](#安装和配置)
- [书单管理](#书单管理)
- [精读生成](#精读生成)
- [质检问题](#质检问题)
- [高级使用](#高级使用)
- [故障排除](#故障排除)

---

## 基础问题

### Q: Read Book Skill 是什么？

A: Read Book Skill 是一个AI驱动的读书智能体，可以自动精读书籍并生成15000+字的深度读书笔记。它包含：
- 书单管理系统
- HTML精读笔记生成器
- 自动质检系统
- 完整的7步精读流水线

### Q: 需要什么环境？

A: 
- Python 3.7 或更高版本
- 仅使用Python标准库，无需额外安装
- 支持 Windows、macOS、Linux

### Q: 完全免费吗？

A: 是的，本项目采用MIT许可证，完全免费开源。但使用AI（如Claude）生成内容可能需要API费用。

### Q: 支持哪些书籍？

A: 理论上支持所有书籍。AI会根据书籍内容生成精读笔记。对于专业性强的书籍，可能需要人工补充。

---

## 安装和配置

### Q: 如何安装？

A: 
```bash
git clone https://github.com/YOUR_USERNAME/read-book-skill.git
cd read-book-skill
python scripts/init_project.py /path/to/your-project
```

### Q: 需要安装依赖吗？

A: 不需要。核心功能仅使用Python标准库。`requirements.txt` 仅用于说明Python版本要求。

### Q: 如何修改字数限制？

A: 需要同步修改以下文件：
1. `scripts/qc_check.py` - 质检阈值
2. `scripts/init_project.py` - 配置模板
3. `scripts/html_template.py` - 提示文案
4. `SKILL.md` - 文档说明
5. `references/pipeline.md` - 流水线文档
6. `references/quality_standard.md` - 质检标准

### Q: 如何自定义HTML样式？

A: 编辑 `book_config.json` 中的 `html_style` 部分：

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

也可以修改 `scripts/html_template.py` 中的CSS样式。

---

## 书单管理

### Q: 如何添加书籍？

A: 
```bash
python scripts/book_manager.py add "书名" \
  --author "作者" \
  --priority 高 \
  --tags "标签1,标签2"
```

### Q: 如何批量导入书单？

A: 编辑 `book_list.json` 文件，按格式添加：

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

### Q: 选书规则是什么？

A: 默认规则：
1. 优先级：高 > 中 > 低
2. 同优先级内，优先选未读的（last_read为null）
3. 全部已读时，选最早读的

可在 `book_config.json` 中自定义规则。

### Q: 如何查看书单统计？

A: 
```bash
python scripts/book_manager.py stats
```

输出JSON格式的统计信息，包括总数、已读、未读、优先级分布、标签统计等。

---

## 精读生成

### Q: 精读笔记包含哪些内容？

A: 15个模块：
1. 🏆 荣誉与口碑
2. ✍️ 作者简介
3. 👥 目标读者与阅读价值
4. 🌐 创作背景
5. 🔬 核心理论逐章拆解（最核心，5000字）
6. 📌 实用案例
7. 💭 读者笔记精选
8. 📊 关键数据与事实
9. 💎 金句摘录
10. 🧠 作者底层逻辑
11. 📈 可视化图表总结
12. 🎯 落地实践指南
13. 🔗 跨书关联
14. ⚖️ 客观评价
15. 📖 一页精华

### Q: 如何生成精读笔记？

A: 完整流程：
```bash
# 1. 选书
python scripts/book_manager.py select --title "书名"

# 2. 生成骨架
python scripts/html_template.py generate \
  --title "书名" \
  --author "作者" \
  --task-id book_20260827_1200

# 3. AI填充内容（需要Claude等AI）

# 4. 质检
python scripts/qc_check.py book_cache/book_raw_content/book_20260827_1200.html

# 5. 更新状态
python scripts/book_manager.py update "书名"
```

### Q: 为什么需要分2-3次写入？

A: 因为15000字的内容量很大，单次写入容易截断。建议按模块分批写入：
- 第一批：模块①-⑤（约6000字）
- 第二批：模块⑥-⑪（约5000字）
- 第三批：模块⑫-⑮（约4000字）

### Q: 如何确保内容质量？

A: 遵循以下原则：
- 每个观点都要有"为什么"
- 案例要讲细节（人物、时间、冲突、转折、结果）
- 数据要有解读（数字本身不说明问题）
- 时刻回答"所以呢"（So what）
- 章节间要有联系

---

## 质检问题

### Q: 质检失败怎么办？

A: 查看FAIL项，针对性补充：

| FAIL项 | 解决方法 |
|--------|----------|
| 字数不足 | 补充更多内容 |
| 模块缺失 | 检查15个模块是否都有内容 |
| 模块无内容 | 每模块≥200字实质内容 |
| 图表不足 | 添加CSS图表 |
| 章节卡不足 | 添加chapter-card |
| 金句不足 | 添加blockquote |
| 数据行不足 | 添加tr |
| 行动建议不足 | 在落地实践指南中添加li |
| 占位符残留 | 替换所有【...】 |
| HTML未闭合 | 确保以</html>结尾 |
| 重复注水 | 每段写不同内容 |

### Q: 如何查看质检详情？

A: 
```bash
python scripts/qc_check.py book_cache/book_raw_content/book_20260827_1200.html
```

输出示例：
```
[OK ] book_cache/book_raw_content/book_20260827_1200.html
    words=17303 modules=15/15(内容) charts=4种/72容器 cards=10 bq=14 tr=16 action_li=9 closed=True ph=0
```

### Q: 质检标准是什么？

A: 11项检查：
1. 字数 ≥ 15000
2. 15个模块全部存在
3. 每模块≥200字实质内容
4. ≥4种有效图表
5. 章节卡≥8
6. 金句≥12
7. 数据表行≥12
8. 行动建议≥6
9. 无占位符残留
10. HTML闭合
11. 无重复注水

### Q: 如何修复"模块有标题无内容"？

A: 在每个模块标题后添加≥200字的实质内容。例如：

```html
<h2>① 🏆荣誉与口碑</h2>
<ul class="honor-list">
  <li><strong>豆瓣评分：</strong>8.5分，超过90%的读者给出4星以上评价...</li>
  <li><strong>名人荐读：</strong>查理·芒格推荐为"必读商业经典"...</li>
  <!-- 更多内容... -->
</ul>
```

---

## 高级使用

### Q: 如何批量阅读多本书？

A: 使用Claude Code时可以说：
```
帮我读3本书
```

或者手动循环执行Step 0-7，每次选不同的书。

### Q: 如何自定义Agent提示词？

A: 编辑 `agent_prompt/main_orchestrator.md`，定义你的精读流程。

### Q: 如何集成到现有系统？

A: 可以通过以下方式集成：
1. 作为Claude Code的skill使用
2. 调用Python脚本的命令行接口
3. 导入Python模块作为库使用

### Q: 如何扩展质检规则？

A: 在 `scripts/qc_check.py` 中：
1. 添加检查函数
2. 在 `qc()` 函数中调用
3. 添加对应的测试用例
4. 更新文档

### Q: 如何修改HTML模板？

A: 在 `scripts/html_template.py` 中：
1. 修改 `HTML_TEMPLATE` 变量
2. 更新 `references/html_visual_standard.md`
3. 运行测试确保无语法错误

---

## 故障排除

### Q: 运行脚本时报错"ModuleNotFoundError"

A: 确保使用正确的Python版本（3.7+），并在项目目录下运行脚本。

### Q: 质检时提示"文件不存在"

A: 检查文件路径是否正确，确保HTML文件已生成。

### Q: 生成的HTML文件乱码

A: 确保使用UTF-8编码：
```bash
python scripts/html_template.py generate --title "书名" --author "作者" --task-id book_20260827_1200
```

### Q: 质检结果不准确

A: 检查以下几点：
1. 是否使用了正确的质检脚本
2. HTML文件是否完整
3. 是否有语法错误

### Q: 如何恢复删除的书籍？

A: 如果有备份，直接恢复 `book_list.json`。否则需要重新添加。

### Q: 项目目录损坏怎么办？

A: 重新初始化：
```bash
python scripts/init_project.py /path/to/new-project
```

然后将旧的 `book_list.json` 复制到新项目。

---

## 性能优化

### Q: 如何加快质检速度？

A: 
1. 使用SSD硬盘
2. 减少HTML文件大小
3. 使用 `--json` 参数减少输出

### Q: 如何减少内存占用？

A: 
1. 避免同时打开多个大HTML文件
2. 定期清理 `book_cache/` 目录
3. 使用流式处理大文件

---

## 安全相关

### Q: 生成的HTML文件安全吗？

A: 是的，生成的HTML文件是静态的，不包含JavaScript或外部资源。

### Q: 如何保护隐私？

A: 
1. 不要在书单中添加敏感信息
2. 定期清理 `book_cache/book_log/` 目录
3. 使用 `.gitignore` 忽略缓存文件

---

## 获取更多帮助

- 📖 查看 [README.md](README.md)
- 🚀 查看 [快速开始指南](GETTING_STARTED.md)
- 🤝 查看 [贡献指南](CONTRIBUTING.md)
- 🐛 报告问题：GitHub Issues
- 💬 讨论交流：GitHub Discussions

---

**还有问题？** 在GitHub Issues中提问，我们会尽快回复！ 🙋‍♂️
