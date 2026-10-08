# 快速开始

核心就一句话：**装一次，之后全靠对话。**

不需要创建项目、不需要指定目录、不需要执行任何初始化 —— skill 目录本身就是工作区。
第一次用到的时候会自动生成空的 `book_list.json` 和 `book_cache/`（不会塞任何示例书）。

前置条件：Python 3.7+（脚本只用标准库，无需装任何依赖）。

---

## 第一步：安装（每台机器只做一次）

### 方式 A：把链接发给 AI，让它装（推荐，不用碰命令行）

对 OpenClaw / Claude / Cursor 等任意工具说一句：

```
帮我安装这个 skill：https://github.com/xiaojinglong/deep-read-agent-skill
```

AI 会自己 clone 到该工具的 skills 目录。**你不需要跑 install.py。**

### 方式 B：自己装

在 skill 目录下执行：

```bash
python install.py
```

会交互式询问目标位置。也可以一次装到所有支持的平台：

```bash
python install.py --targets all
python install.py --list        # 先看支持哪些平台
```

支持的目标：`agents`（通用 `.agents/skills/`，多数工具都读它）、`claude`、`openclaw`、
`workbuddy`、`codex`、`gemini`、`cursor`、`opencode`。

> 说明：装到多个位置后，**各位置的书单相互独立**。你只在单一工具里用时完全无感；
> 如果今天在 A 工具加书、明天在 B 工具读书，两边会各记各的。
> 需要统一的话改共享数据目录即可。

**也可以完全不用命令行** —— 直接把 skill 文件夹复制到你的工具的 skills 目录里（例如
`~/.claude/skills/read-book-skill/`）同样生效，因为本 skill 用的是相对路径，不依赖任何
模板变量替换。

---

## 第二步：读书（日常使用，一句话搞定）

装好之后，**新开一个会话**，直接说话：

```
帮我读《穷查理宝典》
```

以下说法都能被理解：

- "读一本" / "精读一本" —— 按优先级自动挑一本未读的
- "读 3 本" —— 循环执行，每本生成独立笔记
- "再读一遍《原则》" —— 指定书名
- "书单里还有什么没读的" —— 只查询，不生成笔记

说完就等着。AI 会自动跑完 4 个阶段，全程不需要你参与：

| 阶段 | AI 做什么 |
|------|----------|
| 选书 | 高优先级 + 未读优先；同名多本时精确匹配，不误伤 |
| 核验事实 | **强制联网**核验豆瓣评分、出版信息、作者履历、**全书章节目录**，写进 `book_cache/book_meta/*_facts.md` |
| 生成笔记 | 用模板生成骨架，再填满 15 个模块，目标 15000+ 字 |
| 质检回写 | `qc_check.py` 全项通过才算完；通过后把笔记路径回写到书单 |

不达标会自己补写重跑（最多重试 2 次），最后给你一份摘要 + 笔记文件路径。

### 跑一次会看到什么

实测《穷查理宝典》一次通过的结果：

```
[OK ] book_cache/book_raw_content/book_20261008_1854.html
    words=19719  modules=15/15  charts=5种  cards=14
    bq=22  tr=21  action_li=10  closed=True  ph=0
```

---

## 第三步（可选）：创建一个自己命名的读书智能体

如果你想让不同的智能体管不同的书单 —— 比如一个读历史、一个读商业 —— 就说：

```
创建一个读书智能体，名字叫「给娃读历史」
```

AI 会建一个独立工作区（`agents/给娃读历史/`），有自己的书单和笔记，跟其他智能体互不干扰。

之后要用它就带上名字：

```
用「给娃读历史」帮我精读《孙子兵法》
```

**《孙子兵法》不在书单里也没关系** —— AI 会自动把它加进这个智能体的书单再读。

其他说法：

```
我有哪些读书智能体？
「给娃读历史」里读过哪些书？
把「给娃读历史」删掉吧        ← AI 会先列出要删什么，你确认后才真删
```

不用具名智能体也完全可以，跳过这步直接在 skill 目录里读就行。

---

## 第四步：书单管理（同样是说话）

```
加一本《纳瓦尔宝典》，作者埃里克·乔根森，优先级高，标签财富、幸福
把《原则》的优先级改成中
《人类简史》读完了，删掉吧
我有哪些书？哪些还没读？
```

对应的命令（想手动执行时）：

```bash
python scripts/book_manager.py add "书名" --author "作者" --priority 高 --tags "标签1,标签2"
python scripts/book_manager.py edit "书名" --add-tags "2026目标"
python scripts/book_manager.py remove "书名"          # 只预览，不真删
python scripts/book_manager.py remove "书名" --yes    # 确认后才真删
python scripts/book_manager.py list --unread
python scripts/book_manager.py search "关键词"
python scripts/book_manager.py stats
python scripts/book_manager.py notes --title "书名"   # 按书名找回笔记路径
```

### 几个安全设计，值得知道

- **精确优先**：输入残缺书名若模糊命中多本，会直接拒绝并列出候选，不会出现
  `remove "原则"` 连带删掉《原则生活》这种静默误伤。
- **删除默认只预览**：必须显式加 `--yes` 才真的删。
- **同名会拦截**：重复 `add` 同名书籍会被挡下并提示已存在，确认是另一本再加 `--force`。
- **笔记可找回**：`update` 时带 `--note-path`，路径会写进书单，之后不用去翻
  `book_20261008_1854.html` 这种文件名。

---

## 数据都存在哪

全部在 skill 目录内，直接删掉 skill 目录就彻底卸载：

```
book_list.json                              书单（含每本书的笔记路径）
book_cache/book_meta/${task_id}.json        本次选书元数据
book_cache/book_meta/${task_id}_facts.md    联网核验的事实清单
book_cache/book_raw_content/${task_id}.html 精读笔记成品
book_cache/book_log/${task_id}.log          本次运行日志
```

笔记 HTML 自带完整 CSS，单文件独立，可以直接分享。

---

## 常见问题

**Q：一定要先初始化项目吗？**
不用。只有当你想把书单和笔记单独存放、脱离 skill 目录时，才用
`python scripts/init_project.py <目录>` 导出一份独立工作区。

**Q：质检失败怎么办？**
AI 会自动补写重跑。想手动排查就跑 `python scripts/qc_check.py <html>`，
它会直接列出 FAIL 项和未替换的占位符。

**Q：换了台电脑，书单能带走吗？**
能。复制 `book_list.json` 即可；`book_cache/` 一起复制则笔记也带走。
重装时加 `--force` 会覆盖数据文件，默认不覆盖。

**Q：装了之后 AI 没反应？**
多数工具需要新开会话才会加载新技能；OpenClaw 还需要 `openclaw gateway restart`。
另外注意 OpenClaw 会**静默跳过体积过大的 SKILL.md**。

---

## 想批量导入书单

直接编辑 `book_list.json`：

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

`priority` 只能是 `高` / `中` / `低`；`notes` 字段由脚本自动维护，不用手写。
