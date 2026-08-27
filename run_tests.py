#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""运行所有单元测试

用法:
    python run_tests.py           # 运行所有测试
    python run_tests.py -v        # 详细输出
    python run_tests.py TestXxx   # 运行特定测试类
"""

import unittest
import sys
import os

# 确保能导入scripts目录
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

if __name__ == '__main__':
    # 自动发现tests目录下的所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2 if '-v' in sys.argv else 1)
    result = runner.run(suite)

    # 返回退出码
    sys.exit(0 if result.wasSuccessful() else 1)
