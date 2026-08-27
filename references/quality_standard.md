# 精读笔记质检标准

## 验收清单

一份合格的精读笔记必须通过以下全部检查：

| # | 检查项 | 阈值 | 说明 |
|---|--------|------|------|
| 1 | 正文字数 | ≥ 15000 | 去除 CSS/style/script/注释/head 后的纯文字字数 |
| 2 | 模块完整 | 15/15 | 15个模块标题全部存在 |
| 3 | 模块有内容 | 15/15 | 每模块标题后 3000 字符内实质文字 ≥ 200 字 |
| 4 | 图表种类 | ≥ 4 种 | chart/timeline/mindmap/flow/radar 中至少4类的容器内有≥80字实质内容 |
| 5 | 章节卡片 | ≥ 8 | `class="chapter-card"` 数量 |
| 6 | 金句 | ≥ 12 | `<blockquote` 数量 |
| 7 | 数据表行 | ≥ 12 | `<tr` 数量 |
| 8 | 行动建议 | ≥ 6 | 落地实践指南到跨书关联之间的 `<li>` 数 |
| 9 | 占位符 | 0 | 无 `【...】`、TODO、待补充、lorem、`{{ }}` 残留 |
| 10 | HTML闭合 | 是 | 文件以 `</html>` 结尾 |
| 11 | 无重复注水 | 是 | 长度≥20的句子不出现≥3次 |

## 字数统计正确方法

**关键：必须先去除 `<style>` 块再统计，否则 CSS 会虚高约 6000 字。**

```python
import re

with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 去除 <style> 块
body = re.sub(r'<style>.*?</style>', '', html, flags=re.S)
# 2. 去除 <head> 块
body = re.sub(r'<head>.*?</head>', '', body, flags=re.S)
# 3. 去除所有 HTML 标签
text = re.sub(r'<[^>]+>', '', body)
# 4. 去除所有空白
text = re.sub(r'\s+', '', text)

print(f'正文纯文字字数: {len(text)}')
```

## 运行质检

```bash
# 单个文件
python scripts/qc_check.py book_cache/book_raw_content/book_20260827_1030.html

# 多个文件
python scripts/qc_check.py book_cache/book_raw_content/*.html
```

输出示例：
```
[OK] book_cache/book_raw_content/book_20260827_1030.html
    words=12800 modules=15/15(内容) charts=5种/8容器 cards=12 bq=15 tr=14 action_li=7 closed=True ph=0

1/1 passed
```

未通过时会列出 FAIL 项：
```
[FAIL] book_cache/book_raw_content/book_20260827_1030.html
    words=8500 modules=14/15(内容) charts=3种/5容器 cards=6 bq=8 tr=10 action_li=4 closed=True ph=3
    FAIL项: ['字数>=15000', '模块15/15且有内容', '图表>=4种有效', '章节卡>=8', '金句>=12', '数据行>=12', '行动建议>=6', '无占位符']
```

## 常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 字数虚高6000+ | 没去除 CSS `<style>` 块 | 用正确的统计方法 |
| 模块有标题无内容 | 只填了标题没填内容 | 每模块≥200字实质内容 |
| 图表无效 | 空壳图表容器无实质文字 | 图表容器内≥80字文字解读 |
| 占位符残留 | 骨架模板的 `【...】` 没替换 | 全局搜索替换所有占位符 |
| 重复注水 | 复制粘贴相同句子凑字数 | 每段写不同内容 |
