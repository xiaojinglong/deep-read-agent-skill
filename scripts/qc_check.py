#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读书精读笔记质检脚本 v2（加强版，可移植）

用法:
  python qc_check.py <html_file> [<html_file> ...]
  python qc_check.py --project-dir /path/to/project book_cache/book_raw_content/*.html

验收标准:
  - 字数 >= 15000（去 CSS/style/script/注释/head 后统计纯文字）
  - 15个模块全部存在且有实质内容（每模块标题后3000字符内>=200字）
  - >= 4种有效图表（容器内实质文字>=80字才算有效）
  - 章节卡 >= 8
  - 金句 blockquote >= 12
  - 数据表行 <tr> >= 12
  - 行动建议 <li> >= 6（落地实践指南到跨书关联之间）
  - 无占位符残留（【...】、TODO、待补充、lorem、{{ }}）
  - HTML闭合 </html>
  - 无重复注水（长度>=20的句子出现>=3次判FAIL）
"""
import re
import sys
import os
import argparse
import json
import glob as glob_mod
from collections import Counter

MODULES = ['荣誉与口碑', '作者简介', '目标读者与阅读价值', '创作背景', '核心理论逐章拆解',
           '实用案例', '读者笔记精选', '关键数据与事实', '金句摘录', '作者底层逻辑',
           '可视化图表总结', '落地实践指南', '跨书关联', '客观评价', '一页精华']
CHART_CLASSES = ('chart', 'timeline', 'mindmap', 'flow', 'radar')
# 兜底用的高置信占位符特征词（无法读取模板占位符库时启用）。
# 注意：不能直接用 `【[^】]*】` 全量匹配 —— 那会把正文里正常的
# 【书名】【术语】标注（如「引用了【原则】的观点」）误判成占位符，
# 造成该项永远无法通过。
PLACEHOLDER_HINT_WORDS = (
    '待填写', '待补充', '待添加', '待完善', '占位', '此处插入', '待确认',
    'TODO', 'TBD', 'XXX', 'lorem', '请在此', '自行补充',
)
PLACEHOLDER_PATTERNS = [
    r'\{\{.*?\}\}', r'TODO', r'\bTBD\b', r'lorem', r'待补充', r'此处插入',
    r'待添加', r'待完善', r'待填写', r'占位符',
]
# 子串兜底匹配的最小长度，低于此长度的模板占位符不参与，
# 避免【作者】【说明】【维度】【章节】这类短词误伤正文。
_PH_SUBSTR_MIN = 4


def _load_template_placeholders(script_dir=None):
    """从 html_template.py 提取全部【...】占位符，作为精确比对库。

    模板里的占位符（如【具体说明】【金句原文】【发生了什么，意味着什么】）
    本质是写给 Agent 的写作指令，集合固定且可从模板源文件直接读取。
    用"是否命中该集合"来判断占位符有没有被替换，比泛化的【...】正则
    精确得多：既不会漏判，也不会误伤正文中正常的【书名】【术语】。
    """
    cands = []
    if script_dir:
        cands.append(os.path.join(script_dir, 'html_template.py'))
    cands.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'html_template.py'))
    for c in cands:
        try:
            with open(c, encoding='utf-8') as f:
                found = set(re.findall(r'【[^】]*】', f.read()))
            if found:
                return found
        except OSError:
            continue
    return set()


def _placeholders(html, tpl_ph):
    """返回 (hard_hits, soft_count)

    hard_hits  : 确认未替换的占位符 —— 计入 FAIL
    soft_count : 正文中正常使用的【...】（如【原则】【黑天鹅】）—— 仅提示，不计 FAIL

    判定顺序：
      1. 与模板占位符完全一致             -> hard
      2. 内文包含某个模板占位符的内文     -> hard（覆盖 AI 二次改写的情况）
      3. 内文含高置信占位特征词           -> hard（模板库不可用时的兜底）
      4. 其余                             -> soft
    """
    hard, soft = [], 0
    substr_lib = [t[1:-1] for t in tpl_ph if len(t) - 2 >= _PH_SUBSTR_MIN]
    for raw in re.findall(r'【[^】]*】', html):
        inner = raw[1:-1]
        if raw in tpl_ph:
            hard.append(raw)
        elif any(s in inner for s in substr_lib):
            hard.append(raw)
        elif any(w in inner for w in PLACEHOLDER_HINT_WORDS):
            hard.append(raw)
        else:
            soft += 1
    return hard, soft


def _text_of(html):
    """去 style/script/注释/head 后取纯文字"""
    for pat in (r'<style.*?</style>', r'<script.*?</script>', r'<!--.*?-->', r'<head.*?</head>'):
        html = re.sub(pat, '', html, flags=re.S)
    return re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', html))


def _module_content_ok(html):
    """每个模块标题后 3000 字符内实质文字 >= 200

    修复：优先在 h2 标题中查找模块名，避免在正文中误匹配
    """
    ok = 0
    for m in MODULES:
        # 优先在 h2 标签中查找模块名（格式：① 🏆荣誉与口碑 或包含模块名的h2）
        pattern = r'<h2[^>]*>[^<]*' + re.escape(m) + r'[^<]*</h2>'
        match = re.search(pattern, html)
        if match:
            match_start = match.start()
        else:
            # 备用：直接查找模块名（兼容旧格式）
            idx = html.find(m)
            if idx < 0:
                return False, ok
            match_start = idx
        # 检查模块标题后3000字符内的实质内容
        if len(_text_of(html[match_start:match_start + 3000])) >= 200:
            ok += 1
    return ok == len(MODULES), ok


def _charts_ok(html):
    """至少 4 种图表的容器内有实质内容(>=80字)"""
    kinds, total = set(), 0
    for c in CHART_CLASSES:
        for m in re.finditer(r'class="' + c + r'[^"]*"', html):
            total += 1
            if len(_text_of(html[m.start():m.start() + 600])) >= 80:
                kinds.add(c)
    return len(kinds) >= 4, len(kinds), total


def _action_items(html):
    """落地实践指南 到 跨书关联 之间的 <li> 数

    修复：支持在h2标签中查找模块名（格式：⑫ 🎯落地实践指南）
    """
    # 优先在h2标签中查找
    pattern_a = r'<h2[^>]*>[^<]*落地实践指南[^<]*</h2>'
    pattern_b = r'<h2[^>]*>[^<]*跨书关联[^<]*</h2>'
    match_a = re.search(pattern_a, html)
    match_b = re.search(pattern_b, html)

    if match_a and match_b:
        a, b = match_a.start(), match_b.start()
    else:
        # 备用：直接查找
        a, b = html.find('落地实践指南'), html.find('跨书关联')

    if a < 0 or b < 0 or b <= a:
        return 0

    # 不能直接用 count('<li>')：那要求 li 必须写成裸标签，一旦 Agent 生成
    # <li class="act"> 这种带属性的常规写法就会被全部漏计，直接判 0 条。
    # 这里用正则匹配任意属性的开标签，`(?=[\s>])` 保证不会误吃掉 <link>。
    return len(re.findall(r'<li(?=[\s>/])', html[a:b]))


def _dup_detect(text):
    """长度>=20 的句子出现 >=3 次 → 注水"""
    sents = [s for s in re.split(r'[。！？；.!?;]', text) if len(s) >= 20]
    for s, n in Counter(sents).most_common(3):
        if n >= 3:
            return True, (s[:30], n)
    return False, None


def qc(path, tpl_ph=None):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    if tpl_ph is None:
        tpl_ph = _load_template_placeholders()
    text = _text_of(html)
    words = len(text)
    mods_total = sum(1 for m in MODULES if m in html)
    mods_ok, mods_real = _module_content_ok(html)
    charts_ok, chart_kinds, chart_containers = _charts_ok(html)
    # 同理，不能精确匹配 class="chapter-card"：多 class 写法
    # （class="chapter-card featured"）会被漏计。
    cards = len(re.findall(r'class="[^"]*\bchapter-card\b[^"]*"', html))
    # <blockquote> / <tr> 用前缀计数即可自然兼容带属性的写法
    bq = len(re.findall(r'<blockquote(?=[\s>/])', html))
    trs = len(re.findall(r'<tr(?=[\s>/])', html))
    li = _action_items(html)
    closed = html.strip().endswith('</html>')
    ph_hits, ph_soft = _placeholders(html, tpl_ph)
    ph = len(ph_hits) + sum(len(re.findall(p, html, flags=re.I)) for p in PLACEHOLDER_PATTERNS)
    dup, dup_info = _dup_detect(text)

    checks = {
        '字数>=15000': words >= 15000,
        '模块15/15且有内容': mods_total == 15 and mods_ok,
        '图表>=4种有效': charts_ok,
        '章节卡>=8': cards >= 8,
        '金句>=12': bq >= 12,
        '数据表行>=12': trs >= 12,
        '行动建议>=6': li >= 6,
        '无占位符': ph == 0,
        '</html>闭合': closed,
        '无重复注水': not dup,
    }
    flag = 'OK ' if all(checks.values()) else 'FAIL'
    print(f'[{flag}] {path}')
    print(f'    words={words} modules={mods_real}/15(内容) charts={chart_kinds}种/{chart_containers}容器 '
          f'cards={cards} bq={bq} tr={trs} action_li={li} closed={closed} ph={ph}' +
          (f' DUP:{dup_info}' if dup else ''))
    failed = [k for k, v in checks.items() if not v]
    if failed:
        print(f'    FAIL项: {failed}')
    if ph_hits:
        sample = '、'.join(sorted(set(ph_hits))[:6])
        print(f'    未替换占位符: {len(ph_hits)} 处，例如 {sample}')
    elif ph_soft:
        print(f'    提示: 正文含 {ph_soft} 处【...】方括号标注（视为正常引用，不计失败）')
    return flag == 'OK '


def resolve_project_dir(explicit=None):
    """解析项目根目录"""
    if explicit:
        return os.path.abspath(explicit)
    # 默认: 脚本上级目录
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description="读书精读笔记质检脚本")
    parser.add_argument("files", nargs="*", help="要检查的HTML文件路径")
    parser.add_argument("--project-dir", default=None, help="项目根目录（默认: 脚本上级目录）")
    parser.add_argument("--json", action="store_true", help="输出JSON格式结果")

    args = parser.parse_args()

    # 如果没有指定文件，尝试从项目目录的默认位置查找
    if not args.files:
        project_dir = resolve_project_dir(args.project_dir)
        default_pattern = os.path.join(project_dir, "book_cache", "book_raw_content", "*.html")
        args.files = glob_mod.glob(default_pattern)
        if not args.files:
            print(f"未找到HTML文件。请指定文件路径或确book_cache/book_raw_content/目录下有HTML文件。")
            sys.exit(1)

    results = []
    for p in args.files:
        # 支持相对路径
        if not os.path.isabs(p) and args.project_dir:
            p = os.path.join(resolve_project_dir(args.project_dir), p)
        if not os.path.exists(p):
            print(f"[ERROR] 文件不存在: {p}")
            results.append(False)
            continue
        results.append(qc(p))

    if args.json:
        output = {
            "total": len(results),
            "passed": sum(results),
            "failed": len(results) - sum(results),
            "all_passed": all(results)
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f'\n{sum(results)}/{len(results)} passed')

    sys.exit(0 if all(results) else 1)


if __name__ == '__main__':
    main()
