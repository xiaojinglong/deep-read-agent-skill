# HTML 精读笔记视觉标准 v5

## 整体风格

暖色调精致配色 + 阴影深度 + 渐变 + 15模块emoji标题体系 + 场景步骤心法 + 一页精华复盘。

## 页面基础

| 属性 | 值 |
|------|------|
| 背景 | `#faf9f6`（暖纸色） |
| 卡片底色 | `#ffffff` |
| 正文字号 | 18px（移动端 19px） |
| 行距 | 1.85 倍 |
| 最大宽度 | 820px 居中 |
| 标题字号 | 23px 加粗 |
| 字体栈 | `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif` |

## 色板（精致暖色调）

| CSS 变量 | 色值 | 用途 |
|----------|------|------|
| `--green` | sage green `#5b8a72` | 关键概念/正面观点/核心定义 |
| `--amber` | warm amber `#c8893d` | 注意事项/局限/风险 |
| `--coral` | muted coral `#c75450` | 反对观点/争议/误区 |
| `--slate` | soft slate `#4a7a9a` | 背景信息/补充说明/知识网络 |
| `--lavender` | dusty lavender `#8b6db0` | 读者画像/建议/推荐 |
| `--gold` | warm gold `#b89968` | 金句引用/一页精华/荣誉口碑 |
| `--teal` | deep teal `#3d8a80` | 思维导图分支/雷达图/案例卡片 |

## 组件样式

### 头部 `.header`
- 三色渐变背景：`linear-gradient(135deg, #f5f0e8 0%, #e9f1f6 50%, #f1ebf5 100%)`
- 顶部 5px 彩虹色条：`linear-gradient(90deg, green, amber, slate, lavender)`
- 阴影 `shadow-md`，圆角 16px

### 标题 `h2`
- 23px 加粗，左边框 5px solid slate
- 底部金色短装饰线（30px 宽，5px 高，圆角）

### 色块 `.block`
- 圆角 10px，左侧 5px 色条，`shadow-sm`
- hover：`translateX(2px)` + `shadow-md`
- 类名对照：`.block-green` / `.block-amber` / `.block-coral` / `.block-slate` / `.block-lavender` / `.block-teal` / `.block-gold`
- 内含 `.label` 标签（圆角 6px，半透明白底）

### 金句引用 `blockquote`
- 暖金渐变背景 + 左侧 5px 金色边框
- 大号引号装饰（56px，金色 15% 透明度）
- `.insight` 子元素：上下文解读，虚线分隔

### 表格 `table`
- 渐变表头（slate-bg），斑马纹，hover 高亮
- 圆角 8px，overflow hidden，shadow-sm

### 章节卡片 `.chapter-card`
- 白底 + 左侧 4px 渐变色条（slate→teal）
- hover 阴影增强
- `.ch-num` 标签：slate 底白字圆角

### 条形图 `.chart`
- 容器：白底 + border + shadow-sm + 圆角 12px
- `.bar-row`：flex 布局，label(140px) + track + value(90px)
- `.bar-fill`：渐变填充，支持 `.green/.amber/.coral/.lavender/.gold` 变色
- 5px 宽度过渡动画

### 时间线 `.timeline`
- 左侧 3px 金色竖线
- `.timeline-item`：金色圆点节点（13px，双层边框）
- `.tl-time`：amber 色加粗，`.tl-content`：18px 正文

### 思维导图 `.mindmap`
- `.mindmap-center`：渐变背景 + 2px slate 边框 + 20px 加粗
- `.mindmap-branch`：flex 1 1 45%，teal 顶部边框，shadow-sm

### 流程图 `.flow`
- 垂直排列，`.flow-step`：2px slate 边框 + 渐变背景
- `.flow-arrow`：24px 金色箭头

### 雷达图 `.radar`
- 2列 grid 布局
- `.radar-dot`：18px 圆点，`.on` 变 teal
- `.radar-label` + `.radar-dots` + `.radar-score`

### 汇总卡片 `.summary-card`
- 三色渐变背景 + slate 边框 + shadow-md
- `.summary-item`：金色左边框 + 半透明白底

### 一句话总结 `.one-liner`
- 金色渐变背景 + 2px 金色边框 + 22px 加粗
- 大号引号装饰（64px，金色 12% 透明度）

### 评分卡 `.rating`
- 金色渐变背景 + shadow-sm
- 分数：52px amber 加粗，`/10` 灰色小字
- 星级：amber 色 28px

## v5 新增组件

### 荣誉口碑列表 `.honor-list`
- 无序列表，每项：白底 + 左侧 4px 金色边条 + shadow-sm + 圆角 8px
- 用于模块① 🏆荣誉与口碑

### 读者画像卡片 `.reader-card`
- lavender 色系：左侧 5px 边框 + lavender-bg 背景 + shadow-sm + 圆角 10px
- `.reader-label`：17px lavender 加粗标题（含 emoji 前缀）
- 用于模块③ 👥目标读者与阅读价值的 4 类读者画像

### 实用案例卡片 `.case-card`
- 白底 + 左侧 5px teal 边框 + shadow-sm + 圆角 12px
- h3 标题为 teal 色
- `.case-tip`：一句话启发，amber 色，虚线分隔
- 用于模块⑥ 📌实用案例

### 一页精华复盘块 `.recap`
- 金色渐变背景 + 2px 金色边框 + shadow-md + 圆角 14px
- 段落 18px，`strong` 为 amber 色
- `.recap-summary`：居中 20px 加粗，虚线金色分隔
- 四段式：核心价值 → 最大收获 → 规避误区 → 一句话总结
- 用于模块⑮ 📖一页精华（极简复盘）

## 模块 Emoji 标题体系

每个模块的 h2 标题以 emoji 前缀开头，形成视觉导航系统：

| Emoji | 模块 | 语义 |
|-------|------|------|
| 🏆 | 荣誉与口碑 | 奖杯-荣誉 |
| ✍️ | 作者简介 | 书写-创作 |
| 👥 | 目标读者与阅读价值 | 人群-读者 |
| 🌐 | 创作背景 | 地球-时代背景 |
| 🔬 | 核心理论逐章拆解 | 显微镜-深度分析 |
| 📌 | 实用案例 | 图钉-标记 |
| 💭 | 读者笔记精选 | 思考气泡-笔记 |
| 📊 | 关键数据与事实 | 图表-数据 |
| 💎 | 金句摘录 | 钻石-精华 |
| 🧠 | 作者底层逻辑 | 大脑-逻辑 |
| 📈 | 可视化图表总结 | 趋势线-图表 |
| 🎯 | 落地实践指南 | 靶心-落地 |
| 🔗 | 跨书关联 | 链接-关联 |
| ⚖️ | 客观评价 | 天平-评价 |
| 📖 | 一页精华 | 书-精华 |

## 核心理论模块格式（场景→步骤→心法）

模块⑤ 核心理论逐章拆解采用统一的工具拆解格式：

```
📍 场景：[书中应用场景描述]
Step1（步骤名）：说明 → 结论
Step2（步骤名）：说明 → 结论
心法：[一句话凝练总结]
```

每个工具/模型使用 `.chapter-card` 包裹，含 `.ch-num` 编号标签。

## 响应式（移动端 ≤600px）

- 正文字号 19px，容器内边距减小
- 标题缩小（h1: 28px, h2: 23px, h3: 20px）
- 思维导图分支变为 100% 宽度单列
- 雷达图变为单列
- 条形图 label/value 缩窄
