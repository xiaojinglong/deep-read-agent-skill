#!/usr/bin/env python3
"""读书智能体 - HTML精读笔记模板生成器 v5（可移植版 · 15模块优化版）

参考 workbuddy 精读笔记页面排版优化：15模块结构 + emoji标题体系 + 场景步骤心法 + 一页精华复盘。

Usage:
  python html_template.py generate --title "书名" --author "作者" --task-id book_20260827_1030
  python html_template.py generate --title "书名" --author "作者" --task-id book_20260827_1030 --project-dir /path/to/project
"""

import json
import os
import argparse
import re
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))


def resolve_project_dir(explicit=None):
    if explicit:
        return os.path.abspath(explicit)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="精读笔记 | 《{title}》- {author}：荣誉口碑、作者简介、目标读者、创作背景、核心理论逐章拆解、实用案例、关键数据、金句摘录、底层逻辑、落地指南、跨书关联、客观评价、一页精华">
<title>精读笔记 | 《{title}》- {author}</title>
<style>
  :root {
    --bg: #faf9f6;
    --bg-card: #ffffff;
    --text: #2c2c2c;
    --text-secondary: #6b6b6b;
    --text-tertiary: #9a9a9a;
    --border: #e8e5e0;
    --border-light: #f0ede8;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.10);
    --green: #5b8a72; --green-bg: #ecf3ef; --green-light: #d4e6dc;
    --amber: #c8893d; --amber-bg: #fdf5ea; --amber-light: #f5dfb8;
    --coral: #c75450; --coral-bg: #faeae8; --coral-light: #f0c9c7;
    --slate: #4a7a9a; --slate-bg: #e9f1f6; --slate-light: #c8ddea;
    --lavender: #8b6db0; --lavender-bg: #f1ebf5; --lavender-light: #ddccea;
    --gold: #b89968; --gold-bg: #f8f4ec; --gold-light: #ece0c8;
    --teal: #3d8a80; --teal-bg: #e6f2f0; --teal-light: #b8dedb;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: var(--bg); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; font-size: 20px; line-height: 1.9; color: var(--text); }
  .container { max-width: 820px; margin: 0 auto; padding: 40px 28px 80px; }
  .header { text-align: center; padding: 56px 32px 40px; background: linear-gradient(135deg, #f5f0e8 0%, #e9f1f6 50%, #f1ebf5 100%); border-radius: 16px; margin-bottom: 40px; box-shadow: var(--shadow-md); position: relative; overflow: hidden; }
  .header::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 5px; background: linear-gradient(90deg, var(--green), var(--amber), var(--slate), var(--lavender)); }
  .header h1 { font-size: 34px; font-weight: 800; margin-bottom: 14px; letter-spacing: 2px; color: var(--text); }
  .header .meta { font-size: 17px; color: var(--text-secondary); margin-top: 10px; }
  .header .meta span { margin: 0 8px; }
  .header .date { font-size: 15px; color: var(--text-tertiary); margin-top: 6px; }
  h2 { font-size: 27px; font-weight: 700; margin: 52px 0 22px; padding: 4px 0 4px 18px; border-left: 5px solid var(--slate); position: relative; }
  h2::after { content: ''; display: block; position: absolute; left: -5px; bottom: -4px; width: 30px; height: 5px; border-radius: 3px; background: var(--gold); }
  h3 { font-size: 22px; font-weight: 600; margin: 32px 0 16px; }
  p { margin: 12px 0; }
  strong { font-weight: 600; }
  em { font-style: italic; color: var(--text-secondary); }
  ul, ol { margin: 12px 0 12px 26px; }
  li { margin: 6px 0; }
  .block { padding: 18px 22px; margin: 18px 0; border-radius: 10px; border-left: 5px solid; box-shadow: var(--shadow-sm); transition: transform 0.15s ease, box-shadow 0.15s ease; }
  .block:hover { transform: translateX(2px); box-shadow: var(--shadow-md); }
  .block-green { background: var(--green-bg); border-color: var(--green); }
  .block-amber { background: var(--amber-bg); border-color: var(--amber); }
  .block-coral { background: var(--coral-bg); border-color: var(--coral); }
  .block-slate { background: var(--slate-bg); border-color: var(--slate); }
  .block-lavender { background: var(--lavender-bg); border-color: var(--lavender); }
  .block-teal { background: var(--teal-bg); border-color: var(--teal); }
  .block-gold { background: var(--gold-bg); border-color: var(--gold); }
  .block .label { font-size: 16px; font-weight: 700; margin-bottom: 8px; display: inline-block; padding: 2px 10px; border-radius: 6px; background: rgba(255,255,255,0.6); }
  blockquote { background: linear-gradient(135deg, var(--gold-bg) 0%, #fdfcfa 100%); border-left: 5px solid var(--gold); padding: 24px 28px; margin: 24px 0; border-radius: 8px; font-style: italic; position: relative; box-shadow: var(--shadow-sm); }
  blockquote::before { content: '\201C'; position: absolute; top: 8px; left: 12px; font-size: 56px; color: var(--gold); opacity: 0.15; font-family: Georgia, serif; line-height: 1; }
  blockquote p { margin: 8px 0; position: relative; z-index: 1; }
  blockquote .source { font-size: 16px; color: var(--text-tertiary); font-style: normal; text-align: right; margin-top: 12px; }
  blockquote .insight { font-style: normal; font-size: 17px; color: var(--text-secondary); margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--border); }
  table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 17px; border-radius: 8px; overflow: hidden; box-shadow: var(--shadow-sm); }
  th, td { border: 1px solid var(--border-light); padding: 12px 16px; text-align: left; }
  th { background: linear-gradient(135deg, var(--slate-bg), #f0f5f9); font-weight: 700; color: var(--slate); }
  tbody tr:nth-child(even) { background: var(--bg); }
  tbody tr:hover { background: var(--slate-bg); }
  .divider { border: none; height: 2px; background: linear-gradient(90deg, transparent, var(--border), transparent); margin: 44px 0; }
  .chapter-card { border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin: 20px 0; background: var(--bg-card); box-shadow: var(--shadow-sm); position: relative; overflow: hidden; transition: box-shadow 0.2s ease; }
  .chapter-card:hover { box-shadow: var(--shadow-md); }
  .chapter-card::before { content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 4px; background: linear-gradient(180deg, var(--slate), var(--teal)); }
  .chapter-card h3 { margin-top: 0; color: var(--slate); padding-left: 8px; }
  .chapter-card .ch-num { display: inline-block; background: var(--slate); color: #fff; font-size: 15px; font-weight: 700; padding: 2px 10px; border-radius: 6px; margin-right: 8px; vertical-align: middle; }
  .tag { display: inline-block; background: var(--slate-bg); color: var(--slate); padding: 3px 14px; border-radius: 14px; font-size: 15px; font-weight: 500; margin: 0 4px 4px 0; }
  .rating { text-align: center; padding: 32px; background: linear-gradient(135deg, var(--gold-bg), #fdfaf3); border-radius: 12px; margin: 24px 0; box-shadow: var(--shadow-sm); }
  .rating .score { font-size: 52px; font-weight: 800; color: var(--amber); line-height: 1.2; }
  .rating .score .max { font-size: 24px; color: var(--text-tertiary); }
  .rating .stars { letter-spacing: 4px; font-size: 28px; color: var(--amber); margin-top: 8px; }
  .chart { margin: 24px 0; padding: 24px; border: 1px solid var(--border); border-radius: 12px; background: var(--bg-card); box-shadow: var(--shadow-sm); }
  .chart-title { font-size: 19px; font-weight: 700; margin-bottom: 18px; text-align: center; color: var(--slate); }
  .bar-row { display: flex; align-items: center; margin: 12px 0; }
  .bar-label { flex: 0 0 140px; font-size: 16px; text-align: right; padding-right: 14px; color: var(--text); }
  .bar-track { flex: 1; background: var(--border-light); border-radius: 6px; height: 24px; position: relative; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 6px; background: linear-gradient(90deg, var(--slate), var(--teal)); min-width: 2%; transition: width 0.5s ease; }
  .bar-fill.green { background: linear-gradient(90deg, var(--green), #7aa88e); }
  .bar-fill.amber { background: linear-gradient(90deg, var(--amber), #dca85c); }
  .bar-fill.coral { background: linear-gradient(90deg, var(--coral), #d9706c); }
  .bar-fill.lavender { background: linear-gradient(90deg, var(--lavender), #a58bc0); }
  .bar-fill.gold { background: linear-gradient(90deg, var(--gold), #ceac7e); }
  .bar-value { flex: 0 0 90px; font-size: 15px; padding-left: 12px; color: var(--text-secondary); font-weight: 500; }
  .timeline { margin: 24px 0; padding-left: 28px; border-left: 3px solid var(--gold); }
  .timeline-item { position: relative; padding: 0 0 28px 28px; }
  .timeline-item::before { content: ''; position: absolute; left: -35px; top: 6px; width: 13px; height: 13px; border-radius: 50%; background: var(--gold); border: 3px solid var(--bg-card); box-shadow: 0 0 0 2px var(--gold); }
  .timeline-item .tl-time { font-size: 16px; font-weight: 700; color: var(--amber); margin-bottom: 4px; }
  .timeline-item .tl-content { font-size: 18px; line-height: 1.7; }
  .mindmap { margin: 24px 0; }
  .mindmap-center { text-align: center; padding: 18px; background: linear-gradient(135deg, var(--slate-bg), var(--teal-bg)); border: 2px solid var(--slate); border-radius: 12px; font-weight: 800; font-size: 20px; margin-bottom: 16px; color: var(--slate); box-shadow: var(--shadow-sm); }
  .mindmap-branches { display: flex; flex-wrap: wrap; gap: 14px; }
  .mindmap-branch { flex: 1 1 45%; border: 1px solid var(--border); border-radius: 10px; padding: 16px 18px; background: var(--bg-card); box-shadow: var(--shadow-sm); border-top: 3px solid var(--teal); }
  .mindmap-branch h4 { font-size: 17px; color: var(--teal); margin-bottom: 8px; font-weight: 700; }
  .mindmap-branch p { font-size: 16px; line-height: 1.7; color: var(--text-secondary); margin: 4px 0; }
  .flow { display: flex; flex-direction: column; align-items: center; margin: 24px 0; }
  .flow-step { border: 2px solid var(--slate); background: linear-gradient(135deg, var(--slate-bg), #f5f9fc); border-radius: 10px; padding: 14px 24px; font-size: 17px; font-weight: 700; text-align: center; max-width: 80%; box-shadow: var(--shadow-sm); color: var(--slate); }
  .flow-step p { margin: 4px 0; font-weight: 400; font-size: 16px; color: var(--text-secondary); }
  .flow-arrow { font-size: 24px; color: var(--gold); margin: 6px 0; line-height: 1; }
  .radar { margin: 24px 0; padding: 24px; border: 1px solid var(--border); border-radius: 12px; background: var(--bg-card); box-shadow: var(--shadow-sm); }
  .radar-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .radar-item { display: flex; align-items: center; gap: 10px; }
  .radar-dots { flex: 1; display: flex; gap: 3px; }
  .radar-dot { width: 18px; height: 18px; border-radius: 50%; background: var(--border); }
  .radar-dot.on { background: var(--teal); }
  .radar-label { flex: 0 0 90px; font-size: 16px; font-weight: 600; color: var(--text); }
  .radar-score { flex: 0 0 36px; font-size: 16px; font-weight: 700; color: var(--teal); text-align: center; }
  .summary-card { background: linear-gradient(135deg, #f5f7fa 0%, var(--slate-bg) 50%, var(--teal-bg) 100%); border: 1px solid var(--slate-light); border-radius: 14px; padding: 28px; margin: 20px 0; box-shadow: var(--shadow-md); }
  .summary-card h3 { margin-top: 0; color: var(--slate); }
  .summary-grid { display: flex; flex-wrap: wrap; gap: 14px; margin: 16px 0; }
  .summary-item { flex: 1 1 100%; border-left: 4px solid var(--gold); padding: 10px 16px; background: rgba(255,255,255,0.75); border-radius: 6px; font-size: 17px; line-height: 1.7; }
  .summary-item strong { color: var(--slate); }
  .one-liner { text-align: center; padding: 32px 28px; background: linear-gradient(135deg, var(--gold-bg) 0%, #fdfaf3 100%); border: 2px solid var(--gold); border-radius: 14px; margin: 28px 0; font-size: 22px; font-weight: 700; line-height: 1.7; color: var(--text); box-shadow: var(--shadow-md); position: relative; }
  .one-liner::before { content: '\201C'; font-size: 64px; color: var(--gold); opacity: 0.12; position: absolute; top: 0; left: 16px; font-family: Georgia, serif; line-height: 1; }
  .footer { text-align: center; padding: 44px 0 0; color: var(--text-tertiary); font-size: 15px; }
  .footer .footer-line { width: 60px; height: 3px; background: var(--gold); margin: 0 auto 16px; border-radius: 2px; }
  @media (max-width: 600px) {
    body { font-size: 19px; }
    .container { padding: 20px 18px 60px; }
    .header { padding: 40px 20px 32px; }
    .header h1 { font-size: 28px; }
    h2 { font-size: 23px; }
    h3 { font-size: 20px; }
    table { font-size: 17px; }
    th, td { padding: 10px 12px; }
    .bar-label { flex: 0 0 96px; font-size: 14px; }
    .bar-value { flex: 0 0 58px; font-size: 14px; }
    .mindmap-branch { flex: 1 1 100%; }
    .radar-grid { grid-template-columns: 1fr; }
    .one-liner { font-size: 20px; padding: 24px 18px; }
    .rating .score { font-size: 42px; }
    .summary-item { font-size: 17px; }
    blockquote { padding: 18px 16px; }
    .chapter-card { padding: 20px 16px; }
  }
  .recap { background: linear-gradient(135deg, var(--gold-bg), #fdfaf3); border: 2px solid var(--gold); border-radius: 14px; padding: 32px 28px; margin: 24px 0; box-shadow: var(--shadow-md); }
  .recap p { margin: 16px 0; font-size: 18px; line-height: 1.8; }
  .recap p strong { color: var(--amber); font-weight: 700; }
  .recap .recap-summary { text-align: center; font-size: 20px; font-weight: 700; margin-top: 20px; padding-top: 20px; border-top: 1px dashed var(--gold); color: var(--text); line-height: 1.7; }
  .honor-list { list-style: none; margin: 16px 0; padding: 0; }
  .honor-list li { padding: 10px 16px; margin: 8px 0; background: var(--bg-card); border-radius: 8px; border-left: 4px solid var(--gold); box-shadow: var(--shadow-sm); font-size: 17px; }
  .reader-card { padding: 18px 22px; margin: 14px 0; border-radius: 10px; border-left: 5px solid var(--lavender); background: var(--lavender-bg); box-shadow: var(--shadow-sm); }
  .reader-card .reader-label { font-size: 17px; font-weight: 700; color: var(--lavender); margin-bottom: 6px; }
  .reader-card p { font-size: 16px; color: var(--text-secondary); margin: 4px 0; }
  .case-card { border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin: 20px 0; background: var(--bg-card); box-shadow: var(--shadow-sm); border-left: 5px solid var(--teal); }
  .case-card h3 { color: var(--teal); margin-top: 0; }
  .case-card .case-tip { font-size: 17px; color: var(--amber); font-weight: 600; margin-top: 12px; padding-top: 12px; border-top: 1px dashed var(--border); }
</style>
</head>
<body>
<div class="container">

  <!-- 头部 -->
  <div class="header">
    <h1>《{title}》</h1>
    <div class="meta">
      <span>✍️ {author}</span>
      <span>·</span>
      <span>{tags}</span>
      <span>·</span>
      <span>优先级: {priority}</span>
    </div>
    <div class="date">📅 精读日期: {date} | {task_id}</div>
  </div>

  <!-- ① 🏆荣誉与口碑 -->
  <h2>① 🏆荣誉与口碑</h2>
  <ul class="honor-list">
    <li><strong>豆瓣评分：</strong>【评分及不同版本差异】</li>
    <li><strong>名人荐读：</strong>【推荐人姓名及评价】</li>
    <li><strong>机构推荐：</strong>【高校课程/企业内训指定教材】</li>
    <li><strong>平台数据：</strong>【微信读书热度/划线密度/读者评价数】</li>
    <li><strong>版本信息：</strong>【初版年份/最新修订版/新增内容】</li>
  </ul>

  <!-- ② ✍️作者简介 -->
  <h2>② ✍️作者简介</h2>
  <p>【身份+头衔+曾任职务+经验年限+核心特点。150字，要有血有肉，讲清作者是什么样的人、凭什么写这本书。有转折性事件要讲细节。】</p>
  <h3>跨界身份</h3>
  <ul>
    <li><strong>维度1：</strong>【如：管理咨询——说明】</li>
    <li><strong>维度2：</strong>【如：时评写作——说明】</li>
    <li><strong>维度3：</strong>【如：财务管理——说明】</li>
    <li><strong>维度4：</strong>【如：教学培训——说明】</li>
  </ul>
  <h3>写作动机</h3>
  <blockquote>
    <p>"【作者原话，说明写这本书的动机和初衷】"</p>
    <p class="source">—— {author}</p>
  </blockquote>
  <p>【补充评价：作者的核心写作风格和思想流派定位】</p>

  <!-- ③ 👥目标读者与阅读价值 -->
  <h2>③ 👥目标读者与阅读价值</h2>
  <h3>这本书适合谁读？</h3>
  <div class="reader-card">
    <div class="reader-label">🌱 读者类型1（如：基层从业者）</div>
    <p>【如果...痛点描述 → ...是你的...解决方案 → 延伸收获】</p>
  </div>
  <div class="reader-card">
    <div class="reader-label">📊 读者类型2（如：中层管理者）</div>
    <p>【如果...痛点描述 → ...是你的...解决方案 → 延伸收获】</p>
  </div>
  <div class="reader-card">
    <div class="reader-label">🎯 读者类型3（如：高层决策者）</div>
    <p>【如果...痛点描述 → ...是你的...解决方案 → 延伸收获】</p>
  </div>
  <div class="reader-card">
    <div class="reader-label">💼 读者类型4（如：跨界学习者）</div>
    <p>【如果...痛点描述 → ...是你的...解决方案 → 延伸收获】</p>
  </div>

  <h3>阅读本书能带来的具体收获</h3>
  <ol>
    <li><strong>收获1：</strong>【具体说明】</li>
    <li><strong>收获2：</strong>【具体说明】</li>
    <li><strong>收获3：</strong>【具体说明】</li>
    <li><strong>收获4：</strong>【具体说明】</li>
    <li><strong>收获5：</strong>【具体说明】</li>
  </ol>

  <h3>实际应用价值</h3>
  <div class="block block-green">
    <p><strong>对个人：</strong>【读完能改变什么——观念、行为、技能】</p>
    <p><strong>对组织：</strong>【对团队/企业的管理实践有什么帮助】</p>
  </div>

  <!-- ④ 🌐创作背景 -->
  <h2>④ 🌐创作背景</h2>
  <h3>时代背景</h3>
  <p>【核心命题叩问：这本书回应的是什么时代问题？】</p>
  <ul>
    <li><strong>趋势1：</strong>【如：数字化冲击——说明】</li>
    <li><strong>趋势2：</strong>【如：行业变革——说明】</li>
    <li><strong>趋势3：</strong>【如：全球化影响——说明】</li>
  </ul>
  <h3>故事原型</h3>
  <p>【如果有故事原型/人物原型，讲清背景设定和主人公成长路径。如果是理论书，讲清理论诞生的学术土壤。】</p>
  <h3>写作手法</h3>
  <p><strong>体裁特色：</strong>【叙事还是论证？有什么创新？】</p>
  <p><strong>结构设计：</strong>【全书怎么组织的，为什么这样组织】</p>
  <p><strong>视角选择：</strong>【从什么角度切入，为什么】</p>

  <!-- ⑤ 🔬核心理论逐章拆解 -->
  <h2>⑤ 🔬核心理论逐章拆解</h2>
  <p>【本模块是全文核心，要求覆盖全书所有章节/核心模型，每个工具/模型配以书中真实场景、核心步骤与可迁移心法。按维度或章节组织，有多少就写多少——不许只挑3个。】</p>

  <div class="chapter-card">
    <h3><span class="ch-num">1</span>工具/模型名称（英文/缩写）</h3>
    <p><strong>📍 场景：</strong>【1-2句书中应用场景描述】</p>
    <p><strong>Step1（步骤名）：</strong>说明 → 结论</p>
    <p><strong>Step2（步骤名）：</strong>说明 → 结论</p>
    <p><strong>Step3（步骤名）：</strong>说明 → 结论</p>
    <p><strong>Step4（步骤名）：</strong>说明 → 结论</p>
    <p><strong>心法：</strong>【一句话凝练总结，可迁移的核心智慧】</p>
    <p><strong>关键数据：</strong>【本章出现的关键数据】</p>
    <p><strong>与其他章节关联：</strong>【这章在全书中的位置，为后续什么内容做了铺垫】</p>
  </div>

  <!-- ⑥ 📌实用案例 -->
  <h2>⑥ 📌实用案例</h2>
  <p>【摘自书中实战案例，展示核心逻辑与架构。每个案例含图表拆解和一句话启发。】</p>

  <div class="case-card">
    <h3>案例1｜案例名称</h3>
    <p>【副标题/模型公式行】</p>
    <p><strong>看这张表/图：</strong>【拆解说明——加粗术语后接解释，多个维度用分号连接】</p>
    <p class="case-tip">💡 一句话启发：【凝练总结】</p>
  </div>

  <!-- ⑦ 💭读者笔记精选 -->
  <h2>⑦ 💭读者笔记精选</h2>
  <p>【本书在阅读平台上的读者划线和批注精选，按主题归类呈现。划线是原书精华，批注是读者的真实思考。】</p>

  <h3>🔑 主题分类1（如：晋升与职业发展）</h3>
  <blockquote>
    <p>📖 第X章 · 划线</p>
    <p>"【原文引用】"</p>
    <p class="insight">📖 第X章 · 💬 读者思考："【读者批注】"</p>
  </blockquote>

  <h3>🗣️ 主题分类2（如：沟通与表达）</h3>
  <blockquote>
    <p>📖 第X章 · 划线</p>
    <p>"【原文引用】"</p>
  </blockquote>

  <!-- ⑧ 📊关键数据与事实 -->
  <h2>⑧ 📊关键数据与事实</h2>
  <h3>书中核心数据</h3>
  <ul>
    <li><strong>指标1：</strong>数据 + 对比 + 结论【这个数字说明了什么】</li>
    <li><strong>指标2：</strong>数据 + 对比 + 结论</li>
    <li><strong>指标3：</strong>数据 + 对比 + 结论</li>
  </ul>
  <table>
    <tr><th>数据/事实</th><th>来源章节</th><th>意义解读</th></tr>
    <tr><td>【数据1】</td><td>【章节】</td><td>【这个数字说明了什么，对论证有什么支撑作用】</td></tr>
    <tr><td>【数据2】</td><td>【章节】</td><td>【意义解读】</td></tr>
  </table>

  <!-- ⑨ 💎金句摘录 -->
  <h2>⑨ 💎金句摘录</h2>
  <p>【按主题分组，每组3-5条。选那些读完会停顿、会回味的句子。每条附上下文解读。】</p>

  <h3>核心思维升级</h3>
  <blockquote>
    <p>"【金句原文】"</p>
    <p class="insight">【在什么情境下说的、为什么重要、读到这里应该想到什么】</p>
    <p class="source">—— 《{title}》第X章</p>
  </blockquote>

  <h3>职场发展</h3>
  <blockquote>
    <p>"【金句原文】"</p>
    <p class="insight">【上下文解读】</p>
    <p class="source">—— 《{title}》第X章</p>
  </blockquote>

  <!-- ⑩ 🧠作者底层逻辑 -->
  <h2>⑩ 🧠作者底层逻辑</h2>
  <h3>核心因果链</h3>
  <div class="block block-green">
    <span class="label">✅ 底层思维模型</span>
    <p><strong>第一层：</strong>名称（注释）→ 说明</p>
    <p><strong>第二层：</strong>名称（注释）→ 说明</p>
    <p><strong>第三层：</strong>名称（注释）→ 说明</p>
    <p><strong>公式：</strong>【如果作者有可公式化的模型，写出来】</p>
  </div>
  <h3>可迁移法则</h3>
  <div class="block block-slate">
    <span class="label">ℹ️ 法则1：名称</span>
    <p>【2-3段说明。提炼出可以迁移的"思维武器"——问自己：如果用作者的思维方式看待另一个问题，会怎样？】</p>
    <p><strong>适用场景：</strong>【什么情况下用】</p>
    <p><strong>失效场景：</strong>【什么情况下不适用】</p>
  </div>
  <div class="block block-slate">
    <span class="label">ℹ️ 法则2：名称</span>
    <p>【说明】</p>
    <p><strong>适用场景：</strong>【说明】</p>
    <p><strong>失效场景：</strong>【说明】</p>
  </div>
  <h3>作者的隐含世界观</h3>
  <blockquote>
    <p>【用作者的视角看世界，他相信什么、怀疑什么、追求什么。3段，每段一个核心信念。】</p>
  </blockquote>

  <!-- ⑪ 📈可视化图表总结 -->
  <h2>⑪ 📈可视化图表总结</h2>
  <p>【用CSS图表把全书核心内容可视化，至少4种图表形式。每个图表配文字解读。】</p>

  <div class="chart">
    <div class="chart-title">【图表标题：如 全书核心观点权重图】</div>
    <div class="bar-row">
      <div class="bar-label">【标签】</div>
      <div class="bar-track"><div class="bar-fill green" style="width: 85%;"></div></div>
      <div class="bar-value">【数值/说明】</div>
    </div>
    <div class="bar-row">
      <div class="bar-label">【标签】</div>
      <div class="bar-track"><div class="bar-fill amber" style="width: 70%;"></div></div>
      <div class="bar-value">【数值/说明】</div>
    </div>
  </div>

  <div class="timeline">
    <div class="timeline-item">
      <div class="tl-time">【时间/阶段】</div>
      <div class="tl-content">【发生了什么，意味着什么】</div>
    </div>
    <div class="timeline-item">
      <div class="tl-time">【时间/阶段】</div>
      <div class="tl-content">【发生了什么，意味着什么】</div>
    </div>
  </div>

  <div class="mindmap">
    <div class="mindmap-center">【全书核心主题】</div>
    <div class="mindmap-branches">
      <div class="mindmap-branch">
        <h4>【分支1】</h4>
        <p>【要点说明】</p>
      </div>
      <div class="mindmap-branch">
        <h4>【分支2】</h4>
        <p>【要点说明】</p>
      </div>
    </div>
  </div>

  <div class="radar">
    <div class="chart-title">【雷达图标题：如 全书多维评价】</div>
    <div class="radar-grid">
      <div class="radar-item">
        <span class="radar-label">【维度】</span>
        <div class="radar-dots">
          <div class="radar-dot on"></div><div class="radar-dot on"></div><div class="radar-dot on"></div><div class="radar-dot on"></div><div class="radar-dot"></div>
        </div>
        <span class="radar-score">4/5</span>
      </div>
      <div class="radar-item">
        <span class="radar-label">【维度】</span>
        <div class="radar-dots">
          <div class="radar-dot on"></div><div class="radar-dot on"></div><div class="radar-dot on"></div><div class="radar-dot"></div><div class="radar-dot"></div>
        </div>
        <span class="radar-score">3/5</span>
      </div>
    </div>
  </div>

  <!-- ⑫ 🎯落地实践指南 -->
  <h2>⑫ 🎯落地实践指南</h2>
  <h3>立刻践行的具体动作</h3>
  <ol>
    <li><strong>动作1（模型名）：</strong>【做什么→怎么做→什么时候做→预期效果】</li>
    <li><strong>动作2（模型名）：</strong>【做什么→怎么做→什么时候做→预期效果】</li>
    <li><strong>动作3：</strong>【具体描述】</li>
    <li><strong>动作4：</strong>【具体描述】</li>
    <li><strong>动作5：</strong>【具体描述】</li>
    <li><strong>动作6：</strong>【具体描述】</li>
  </ol>

  <h3>分阶段落地路线图</h3>
  <table>
    <tr><th>阶段</th><th>核心动作</th><th>对应书中工具</th></tr>
    <tr><td>阶段1（如：入门期）</td><td>【核心动作】</td><td>【工具/模型名】</td></tr>
    <tr><td>阶段2（如：成长期）</td><td>【核心动作】</td><td>【工具/模型名】</td></tr>
    <tr><td>阶段3（如：成熟期）</td><td>【核心动作】</td><td>【工具/模型名】</td></tr>
    <tr><td>阶段4（如：精通期）</td><td>【核心动作】</td><td>【工具/模型名】</td></tr>
  </table>

  <h3>复用场景</h3>
  <ul>
    <li>场景1——【工具组合说明】</li>
    <li>场景2——【工具组合说明】</li>
    <li>场景3——【工具组合说明】</li>
  </ul>

  <!-- ⑬ 🔗跨书关联 -->
  <h2>⑬ 🔗跨书关联</h2>
  <p>【书中提及的书目构成阅读地图。说明这本书在知识体系中处于什么位置、读之前应该先读什么、读之后应该接着读什么。】</p>
  <table>
    <tr><th>书名</th><th>作者</th><th>书中关联</th></tr>
    <tr><td>【书名1】</td><td>【作者】</td><td>【与本书的思想关联】</td></tr>
    <tr><td>【书名2】</td><td>【作者】</td><td>【与本书的思想关联】</td></tr>
  </table>
  <div class="block block-slate">
    <span class="label">ℹ️ 阅读建议</span>
    <p>【定位本书为「入口书」还是「进阶书」，推荐优先精读书目】</p>
  </div>

  <!-- ⑭ ⚖️客观评价 -->
  <h2>⑭ ⚖️客观评价</h2>
  <div class="rating">
    <div class="score">【8.5】<span class="max">/10</span></div>
    <div class="stars">★★★★☆</div>
  </div>
  <div class="block block-green">
    <span class="label">✅ 认同之处</span>
    <ul>
      <li><strong>认同1：</strong>【具体到章节的精彩分析】</li>
      <li><strong>认同2：</strong>【具体说明】</li>
      <li><strong>认同3：</strong>【具体说明】</li>
      <li><strong>认同4：</strong>【具体说明】</li>
    </ul>
  </div>
  <div class="block block-amber">
    <span class="label">⚠️ 存疑之处</span>
    <ul>
      <li><strong>存疑1：</strong>【逻辑漏洞或论证薄弱点】</li>
      <li><strong>存疑2：</strong>【过时观点或不适用当下的内容】</li>
      <li><strong>存疑3：</strong>【立场偏差或思维短板】</li>
      <li><strong>存疑4：</strong>【与同类书籍的不足之处】</li>
    </ul>
  </div>
  <div class="block block-lavender">
    <span class="label">💜 最大认知增量</span>
    <p>【读完这本书，最大的认知变化是什么。关键句加粗。要有"原来如此"的感觉。】</p>
  </div>

  <!-- ⑮ 📖一页精华（极简复盘） -->
  <h2>⑮ 📖一页精华（极简复盘）</h2>
  <div class="recap">
    <p><strong>这本书最核心的价值是：</strong>【用2-3句话概述这本书存在的意义——它为读者解决了什么核心问题】</p>
    <p><strong>我最大的收获是：</strong>【3-4个分号分隔的要点，每个要点一句话】</p>
    <p><strong>我需要规避的误区是：</strong>【4-5个分号分隔的要点，落地时容易踩的坑】</p>
    <p class="recap-summary"><strong>一句话总结：</strong>【如果只能记住一句话，是哪句】</p>
  </div>

  <!-- 底部 -->
  <hr class="divider">
  <div class="footer">
    <div class="footer-line"></div>
    <p>读书智能体 v5 | 深度精读笔记自动生成</p>
    <p>{date} | {task_id}</p>
  </div>

</div>
</body>
</html>"""


def generate_html(title, author, task_id, tags="", priority="", project_dir=None, output_subdir="book_cache/book_raw_content"):
    if project_dir is None:
        project_dir = resolve_project_dir()

    output_dir = os.path.join(project_dir, *output_subdir.split("/"))
    os.makedirs(output_dir, exist_ok=True)

    date_str = datetime.now(CST).strftime("%Y-%m-%d")
    html = HTML_TEMPLATE
    for key, val in [("{title}", title), ("{author}", author), ("{tags}", tags),
                     ("{priority}", priority), ("{date}", date_str), ("{task_id}", task_id)]:
        html = html.replace(key, val)

    filename = f"{task_id}.html"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    text = re.sub(r'<[^>]+>', '', html)
    char_count = len(text.replace(' ', '').replace('\n', ''))
    return {
        "file": filepath,
        "filename": filename,
        "skeleton_char_count": char_count,
        "date": date_str,
        "version": "v5",
        "modules": 15,
        "note": "这是骨架模板，Agent需填充内容至15000+字",
    }


def main():
    parser = argparse.ArgumentParser(description="生成HTML精读笔记模板 v5（可移植版 · 15模块优化版）")
    sub = parser.add_subparsers(dest="command")

    p_gen = sub.add_parser("generate", help="生成模板")
    p_gen.add_argument("--title", required=True, help="书名")
    p_gen.add_argument("--author", default="", help="作者")
    p_gen.add_argument("--task-id", required=True, help="任务ID")
    p_gen.add_argument("--tags", default="", help="标签")
    p_gen.add_argument("--priority", default="", help="优先级")
    p_gen.add_argument("--project-dir", default=None, help="项目根目录（默认: 脚本上级目录）")
    p_gen.add_argument("--output-subdir", default="book_cache/book_raw_content", help="输出子目录")

    args = parser.parse_args()
    if args.command == "generate":
        result = generate_html(
            title=args.title,
            author=args.author,
            task_id=args.task_id,
            tags=args.tags,
            priority=args.priority,
            project_dir=args.project_dir,
            output_subdir=args.output_subdir,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
