#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qc_check.py 单元测试"""

import unittest
import sys
import os

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from qc_check import (
    _text_of,
    _module_content_ok,
    _charts_ok,
    _action_items,
    _dup_detect
)


class TestTextOf(unittest.TestCase):
    """测试HTML文本提取"""

    def test_remove_style(self):
        html = '<style>body{color:red}</style><p>正文</p>'
        result = _text_of(html)
        self.assertNotIn('color', result)
        self.assertIn('正文', result)

    def test_remove_script(self):
        html = '<script>alert("test")</script><p>内容</p>'
        result = _text_of(html)
        self.assertNotIn('alert', result)
        self.assertIn('内容', result)

    def test_remove_comments(self):
        html = '<!-- 注释 --><p>正文</p>'
        result = _text_of(html)
        self.assertNotIn('注释', result)
        self.assertIn('正文', result)

    def test_remove_whitespace(self):
        html = '<p>  正  文  </p>'
        result = _text_of(html)
        self.assertEqual(result, '正文')


class TestModuleContentOk(unittest.TestCase):
    """测试模块内容检查"""

    def test_all_modules_present(self):
        # 构建包含所有15个模块的HTML
        modules = ['荣誉与口碑', '作者简介', '目标读者与阅读价值', '创作背景', '核心理论逐章拆解',
                   '实用案例', '读者笔记精选', '关键数据与事实', '金句摘录', '作者底层逻辑',
                   '可视化图表总结', '落地实践指南', '跨书关联', '客观评价', '一页精华']
        html = ""
        for m in modules:
            # 每个模块后面加足够多的内容
            content = "测试内容" * 100  # 400字
            html += f'<h2>① {m}</h2><p>{content}</p>'

        ok, count = _module_content_ok(html)
        self.assertTrue(ok)
        self.assertEqual(count, 15)

    def test_missing_module(self):
        html = '<h2>① 荣誉与口碑</h2><p>内容</p>'
        ok, count = _module_content_ok(html)
        self.assertFalse(ok)

    def test_module_without_content(self):
        html = '<h2>① 荣誉与口碑</h2><p>很少的内容</p>'
        ok, count = _module_content_ok(html)
        self.assertFalse(ok)


class TestChartsOk(unittest.TestCase):
    """测试图表检查"""

    def _make_content(self, min_chars=80):
        """生成足够长的测试内容"""
        return "测试内容文字" * (min_chars // 5 + 1)

    def test_four_charts(self):
        content = self._make_content(80)
        html = f'''
        <div class="chart"><p>{content}</p></div>
        <div class="timeline"><p>{content}</p></div>
        <div class="mindmap"><p>{content}</p></div>
        <div class="flow"><p>{content}</p></div>
        '''
        ok, kinds, total = _charts_ok(html)
        self.assertTrue(ok)
        self.assertEqual(kinds, 4)

    def test_insufficient_charts(self):
        content = self._make_content(80)
        html = f'''
        <div class="chart"><p>{content}</p></div>
        <div class="timeline"><p>{content}</p></div>
        '''
        ok, kinds, total = _charts_ok(html)
        self.assertFalse(ok)
        self.assertEqual(kinds, 2)


class TestActionItems(unittest.TestCase):
    """测试行动建议检查"""

    def test_action_items_in_range(self):
        html = '''
        <h2>落地实践指南</h2>
        <ul>
            <li>行动1</li>
            <li>行动2</li>
            <li>行动3</li>
            <li>行动4</li>
            <li>行动5</li>
            <li>行动6</li>
        </ul>
        <h2>跨书关联</h2>
        '''
        count = _action_items(html)
        self.assertEqual(count, 6)

    def test_action_items_out_of_range(self):
        html = '''
        <h2>落地实践指南</h2>
        <ul><li>行动1</li></ul>
        <h2>跨书关联</h2>
        <ul><li>不在范围内</li></ul>
        '''
        count = _action_items(html)
        self.assertEqual(count, 1)


class TestDupDetect(unittest.TestCase):
    """测试重复注水检测"""

    def test_no_duplication(self):
        text = "这是第一句话。这是第二句话。这是第三句话。"
        is_dup, info = _dup_detect(text)
        self.assertFalse(is_dup)

    def test_with_duplication(self):
        # 重复3次相同的长句子
        sent = "这是一个很长的测试句子用于检测重复注水的情况"
        text = f"{sent}。{sent}。{sent}。"
        is_dup, info = _dup_detect(text)
        self.assertTrue(is_dup)


if __name__ == '__main__':
    unittest.main()
