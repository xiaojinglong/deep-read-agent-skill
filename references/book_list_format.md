# 书单 JSON 格式规范

## book_list.json

读书智能体的书单数据文件，位于项目根目录。

### 数据结构

```json
[
  {
    "title": "书名（必填）",
    "author": "作者名",
    "priority": "高 | 中 | 低",
    "tags": ["标签1", "标签2"],
    "en_slug": "拼音或英文slug",
    "user_read": false,
    "last_read": null
  }
]
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 书籍完整名称 |
| `author` | string | 否 | 作者全名，多人合作用顿号分隔 |
| `priority` | string | 是 | 优先级：`高` / `中` / `低`。选书时 高>中>低 |
| `tags` | string[] | 否 | 分类标签数组，用于按分类筛选 |
| `en_slug` | string | 否 | 拼音/英文标识符，用于文件命名 |
| `user_read` | boolean | 否 | 用户是否已读，默认 false |
| `last_read` | string\|null | 否 | 上次阅读日期 `YYYY-MM-DD`，null 表示未读 |

### 选书规则

1. 优先级排序：高 > 中 > 低
2. 同优先级内，优先选 `last_read` 为 null 的书
3. 全部已读时，选 `last_read` 日期最早的

### 管理命令

```bash
# 选书
python scripts/book_manager.py select                     # 自动选
python scripts/book_manager.py select --title "关键词"      # 指定选
python scripts/book_manager.py select --random             # 随机选

# 更新阅读状态
python scripts/book_manager.py update "书名"

# 列出
python scripts/book_manager.py list                       # 全部
python scripts/book_manager.py list --category "投资"       # 按分类
python scripts/book_manager.py list --priority 高          # 按优先级
python scripts/book_manager.py list --unread              # 只看未读

# 搜索
python scripts/book_manager.py search "关键词"

# 统计
python scripts/book_manager.py stats

# 添加/删除
python scripts/book_manager.py add "书名" --author "作者" --priority 高 --tags "投资,思维"
python scripts/book_manager.py remove "书名"

# 指定项目目录
python scripts/book_manager.py --project-dir /path/to/project stats
```

## 扩展字段（可选）

部分高级用法可使用以下扩展字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `note_file` | string | 精读笔记文件名 |
| `status` | string | 队列状态：`pending` / `completed` |
| `word_count` | int | 笔记字数 |
| `completed_at` | string | 完成日期 |
| `category` | string | 主分类（与 tags[0] 对应） |

## 示例书单

```json
[
  {
    "title": "穷查理宝典",
    "author": "查理·芒格",
    "priority": "高",
    "tags": ["投资", "思维模型"],
    "en_slug": "qiong-cha-li-bao-dian",
    "user_read": false,
    "last_read": null
  },
  {
    "title": "思考，快与慢",
    "author": "丹尼尔·卡尼曼",
    "priority": "高",
    "tags": ["心理学", "决策"],
    "en_slug": "si-kao-kuai-yu-man",
    "user_read": false,
    "last_read": null
  }
]
```
