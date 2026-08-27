# 贡献指南

感谢你对 Read Book Skill 项目的关注！我们欢迎各种形式的贡献。

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [报告问题](#报告问题)
- [提交代码](#提交代码)
- [开发规范](#开发规范)
- [测试要求](#测试要求)
- [文档规范](#文档规范)

## 行为准则

本项目采用开放、包容的态度。请尊重每一位参与者，保持专业和友善的交流。

## 如何贡献

### 1. 报告问题

如果你发现了Bug或有改进建议：

1. 查看 Issues 确认问题未被报告
2. 点击 "New Issue" 创建新问题
3. 使用提供的Issue模板，详细描述问题
4. 如有可能，提供复现步骤和错误信息

### 2. 提交代码

如果你想贡献代码：

1. Fork 本仓库到你的GitHub账号
2. 克隆到本地：
   ```bash
   git clone https://github.com/YOUR_USERNAME/read-book-skill.git
   ```
3. 创建特性分支：
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. 进行开发并测试
5. 提交更改：
   ```bash
   git commit -m "feat: 添加xxx功能"
   ```
6. 推送到你的Fork：
   ```bash
   git push origin feature/your-feature-name
   ```
7. 创建 Pull Request 到主仓库的 `main` 分支

### 3. 改进文档

文档改进同样重要：

- 修正错别字
- 添加使用示例
- 翻译文档
- 补充说明

## 开发规范

### Python代码规范

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用4个空格缩进
- 函数和变量使用snake_case命名
- 类名使用CamelCase命名
- 添加必要的注释和文档字符串

### 提交信息规范

使用语义化提交信息：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型：**
- `feat`: 新功能
- `fix`: 修复Bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例：**
```
feat(book-manager): 添加批量导入书单功能

- 支持从CSV文件导入
- 自动检测重复书籍
- 返回导入统计信息

Closes #123
```

### 分支命名

- `feature/xxx` - 新功能
- `fix/xxx` - Bug修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 重构

## 测试要求

### 编写测试

- 新功能必须添加单元测试
- Bug修复需要添加回归测试
- 测试文件放在 `tests/` 目录
- 文件名以 `test_` 开头

### 运行测试

```bash
# 运行所有测试
python run_tests.py

# 详细输出
python run_tests.py -v

# 运行特定测试类
python run_tests.py TestBookManager

# 运行特定测试方法
python run_tests.py TestBookManager.test_select_book
```

### 测试覆盖率

目标覆盖率：80%以上

```bash
# 安装coverage
pip install coverage

# 运行覆盖率测试
coverage run -m pytest tests/

# 查看报告
coverage report
```

## 文档规范

### 代码文档

- 所有公共函数必须有文档字符串
- 复杂逻辑添加行内注释
- 使用Google或NumPy风格的文档字符串

**示例：**
```python
def select_book(books, title=None, random_pick=False):
    """选书逻辑：优先级 高>中>低, 优先 last_read 为空的
    
    Args:
        books (list): 书籍列表
        title (str, optional): 指定书名。默认为None。
        random_pick (bool, optional): 是否随机选书。默认为False。
    
    Returns:
        dict: 选中的书籍信息，如果未找到返回None
        
    Examples:
        >>> books = [{"title": "测试书", "priority": "高", "last_read": None}]
        >>> select_book(books, title="测试书")
        {"title": "测试书", ...}
    """
```

### README更新

如果修改了功能或添加新特性，请同步更新README.md：

- 功能说明
- 使用示例
- 配置说明
- 常见问题

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/read-book-skill.git
cd read-book-skill
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 核心依赖（仅标准库，无需安装）
pip install -r requirements.txt

# 开发依赖（可选）
pip install pytest coverage black flake8
```

### 4. 运行测试

```bash
python run_tests.py -v
```

### 5. 代码格式化（可选）

```bash
# 使用black格式化
black scripts/ tests/

# 使用flake8检查
flake8 scripts/ tests/
```

## 发布流程

### 版本号规范

采用 [语义化版本](https://semver.org/)：

- `MAJOR.MINOR.PATCH`
- 例：`1.0.0`, `1.1.0`, `1.1.1`

**版本递增规则：**
- `MAJOR`: 不兼容的API修改
- `MINOR`: 向后兼容的功能性新增
- `PATCH`: 向后兼容的问题修正

### 发布步骤

1. 更新版本号（在代码和文档中）
2. 更新CHANGELOG.md
3. 创建Git标签：
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```
4. 在GitHub创建Release

## 常见问题

### Q: 如何添加新的质检规则？

A: 在 `scripts/qc_check.py` 中：
1. 添加检查函数
2. 在 `qc()` 函数中调用
3. 添加对应的测试用例
4. 更新文档

### Q: 如何修改HTML模板样式？

A: 在 `scripts/html_template.py` 中：
1. 修改 `HTML_TEMPLATE` 变量的CSS部分
2. 更新 `references/html_visual_standard.md`
3. 运行测试确保无语法错误

### Q: 如何添加新的书单管理命令？

A: 在 `scripts/book_manager.py` 中：
1. 添加命令处理函数
2. 在 `main()` 中添加argparse子命令
3. 更新SKILL.md的脚本说明
4. 添加测试用例

## 联系方式

- Issues: GitHub Issues
- Discussions: GitHub Discussions

## 致谢

感谢所有为这个项目做出贡献的人！

---

**开始贡献吧！** 🎉
