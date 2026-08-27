#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""book_manager.py 单元测试"""

import unittest
import sys
import os
import json
import tempfile
import shutil

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from book_manager import (
    priority_weight,
    select_book,
    update_last_read,
    add_book,
    to_slug
)


class TestPriorityWeight(unittest.TestCase):
    """测试优先级权重函数"""

    def test_high_priority(self):
        self.assertEqual(priority_weight("高"), 0)

    def test_medium_priority(self):
        self.assertEqual(priority_weight("中"), 1)

    def test_low_priority(self):
        self.assertEqual(priority_weight("低"), 2)

    def test_unknown_priority(self):
        self.assertEqual(priority_weight("未知"), 3)

    def test_empty_priority(self):
        self.assertEqual(priority_weight(""), 3)


class TestSelectBook(unittest.TestCase):
    """测试选书逻辑"""

    def setUp(self):
        self.books = [
            {"title": "书A", "priority": "高", "last_read": None},
            {"title": "书B", "priority": "中", "last_read": None},
            {"title": "书C", "priority": "低", "last_read": "2026-01-01"},
            {"title": "书D", "priority": "高", "last_read": "2026-06-01"},
        ]

    def test_empty_books(self):
        result = select_book([])
        self.assertIsNone(result)

    def test_select_by_title(self):
        result = select_book(self.books, title="书B")
        self.assertEqual(result["title"], "书B")

    def test_select_by_title_not_found(self):
        result = select_book(self.books, title="不存在")
        self.assertIsNone(result)

    def test_select_unread_by_priority(self):
        """应该优先选未读的高优先级书"""
        result = select_book(self.books)
        self.assertEqual(result["title"], "书A")

    def test_select_random_from_unread(self):
        """随机选书应该从未读池中选"""
        result = select_book(self.books, random_pick=True)
        self.assertIn(result["title"], ["书A", "书B"])  # 只有这两本未读

    def test_select_earliest_read(self):
        """全部已读时，选最早读的"""
        all_read = [
            {"title": "书X", "priority": "高", "last_read": "2026-06-01"},
            {"title": "书Y", "priority": "高", "last_read": "2026-01-01"},
        ]
        result = select_book(all_read)
        self.assertEqual(result["title"], "书Y")


class TestUpdateLastRead(unittest.TestCase):
    """测试更新阅读状态"""

    def setUp(self):
        self.books = [
            {"title": "测试书A", "last_read": None, "user_read": False},
            {"title": "测试书B", "last_read": "2026-01-01", "user_read": True},
        ]

    def test_update_existing_book(self):
        count = update_last_read(self.books, "测试书A")
        self.assertEqual(count, 1)
        self.assertIsNotNone(self.books[0]["last_read"])
        self.assertTrue(self.books[0]["user_read"])

    def test_update_nonexistent_book(self):
        count = update_last_read(self.books, "不存在的书")
        self.assertEqual(count, 0)

    def test_update_multiple_matches(self):
        """模糊匹配多本时，都应该更新"""
        books = [
            {"title": "Python编程", "last_read": None, "user_read": False},
            {"title": "Python进阶", "last_read": None, "user_read": False},
        ]
        count = update_last_read(books, "Python")
        self.assertEqual(count, 2)


class TestAddBook(unittest.TestCase):
    """测试添加书籍"""

    def test_add_basic(self):
        books = []
        book = add_book(books, "新书")
        self.assertEqual(len(books), 1)
        self.assertEqual(book["title"], "新书")
        self.assertEqual(book["priority"], "中")
        self.assertFalse(book["user_read"])
        self.assertIsNone(book["last_read"])

    def test_add_with_params(self):
        books = []
        book = add_book(books, "新书", author="作者", priority="高", tags=["标签1"])
        self.assertEqual(book["author"], "作者")
        self.assertEqual(book["priority"], "高")
        self.assertEqual(book["tags"], ["标签1"])


class TestToSlug(unittest.TestCase):
    """测试slug生成"""

    def test_english_title(self):
        result = to_slug("Hello World")
        self.assertEqual(result, "hello_world")

    def test_chinese_title(self):
        result = to_slug("测试标题")
        # 中文字符被转为下划线，连续下划线被合并
        self.assertEqual(result, "_")

    def test_mixed_title(self):
        result = to_slug("Python3编程")
        self.assertIn("python3", result)

    def test_empty_title(self):
        result = to_slug("")
        self.assertEqual(result, "")


if __name__ == '__main__':
    unittest.main()
