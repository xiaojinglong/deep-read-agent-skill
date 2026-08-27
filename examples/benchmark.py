#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read Book Skill 性能基准测试

用法:
    python examples/benchmark.py
    python examples/benchmark.py --iterations 10
"""

import sys
import os
import time
import argparse
import tempfile
import shutil

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


def benchmark_init_project(iterations=5):
    """测试项目初始化性能"""
    print(f"\n📊 测试项目初始化性能 ({iterations}次迭代)...")

    times = []
    for i in range(iterations):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, f"test_project_{i}")
            start = time.time()

            # 导入并运行init_project
            from init_project import init_project
            init_project(target, num_books=5)

            elapsed = time.time() - start
            times.append(elapsed)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"  平均时间: {avg_time:.3f}秒")
    print(f"  最小时间: {min_time:.3f}秒")
    print(f"  最大时间: {max_time:.3f}秒")

    return avg_time


def benchmark_book_manager(iterations=10):
    """测试书单管理性能"""
    print(f"\n📊 测试书单管理性能 ({iterations}次迭代)...")

    # 创建临时项目
    with tempfile.TemporaryDirectory() as tmpdir:
        from init_project import init_project
        init_project(tmpdir, num_books=10)

        # 测试select命令
        times = []
        for i in range(iterations):
            start = time.time()

            from book_manager import load_books, select_book
            books = load_books(tmpdir)
            select_book(books)

            elapsed = time.time() - start
            times.append(elapsed)

        avg_select = sum(times) / len(times)

        # 测试stats命令
        times = []
        for i in range(iterations):
            start = time.time()

            from book_manager import load_books
            from collections import Counter
            books = load_books(tmpdir)
            total = len(books)
            read = sum(1 for b in books if b.get("last_read"))

            elapsed = time.time() - start
            times.append(elapsed)

        avg_stats = sum(times) / len(times)

        print(f"  选书平均时间: {avg_select:.4f}秒")
        print(f"  统计平均时间: {avg_stats:.4f}秒")

        return avg_select, avg_stats


def benchmark_qc_check(iterations=5):
    """测试质检性能"""
    print(f"\n📊 测试质检性能 ({iterations}次迭代)...")

    # 创建临时项目和测试HTML
    with tempfile.TemporaryDirectory() as tmpdir:
        from init_project import init_project
        init_project(tmpdir, num_books=1)

        # 创建测试HTML文件
        html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>测试</title></head>
<body>
<h2>① 🏆荣誉与口碑</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>② ✍️作者简介</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>③ 👥目标读者与阅读价值</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>④ 🌐创作背景</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>⑤ 🔬核心理论逐章拆解</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>⑥ 📌实用案例</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>⑦ 💭读者笔记精选</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>⑧ 📊关键数据与事实</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>⑨ 💎金句摘录</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>⑩ 🧠作者底层逻辑</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>⑪ 📈可视化图表总结</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>⑫ 🎯落地实践指南</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>⑬ 🔗跨书关联</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>⑭ ⚖️客观评价</h2>
<p>""" + "测试内容" * 200 + """</p>
<h2>⑮ 📖一页精华（极简复盘）</h2>
<p>""" + "测试内容" * 200 + """</p>
</body>
</html>"""

        test_file = os.path.join(tmpdir, "test.html")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # 测试质检
        times = []
        for i in range(iterations):
            start = time.time()

            from qc_check import qc
            qc(test_file)

            elapsed = time.time() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        print(f"  质检平均时间: {avg_time:.4f}秒")

        return avg_time


def benchmark_html_template(iterations=5):
    """测试HTML模板生成性能"""
    print(f"\n📊 测试HTML模板生成性能 ({iterations}次迭代)...")

    with tempfile.TemporaryDirectory() as tmpdir:
        times = []
        for i in range(iterations):
            start = time.time()

            from html_template import generate_html
            result = generate_html(
                title="测试书籍",
                author="测试作者",
                task_id=f"benchmark_{i}",
                tags="测试",
                priority="高",
                project_dir=tmpdir
            )

            elapsed = time.time() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        print(f"  生成平均时间: {avg_time:.4f}秒")

        return avg_time


def run_benchmark(iterations=5):
    """运行完整基准测试"""
    print("🚀 Read Book Skill 性能基准测试")
    print("=" * 50)

    # 测试各项性能
    init_time = benchmark_init_project(iterations)
    select_time, stats_time = benchmark_book_manager(iterations * 2)
    qc_time = benchmark_qc_check(iterations)
    template_time = benchmark_html_template(iterations)

    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 性能汇总")
    print("=" * 50)
    print(f"项目初始化: {init_time:.3f}秒")
    print(f"选书操作:   {select_time:.4f}秒")
    print(f"统计操作:   {stats_time:.4f}秒")
    print(f"质检操作:   {qc_time:.4f}秒")
    print(f"模板生成:   {template_time:.4f}秒")

    # 性能评级
    print("\n📈 性能评级:")
    if init_time < 1.0:
        print("  ✓ 项目初始化: 优秀 (< 1秒)")
    elif init_time < 2.0:
        print("  ⚠ 项目初始化: 良好 (1-2秒)")
    else:
        print("  ✗ 项目初始化: 需要优化 (> 2秒)")

    if select_time < 0.01:
        print("  ✓ 选书操作: 优秀 (< 10ms)")
    elif select_time < 0.1:
        print("  ⚠ 选书操作: 良好 (10-100ms)")
    else:
        print("  ✗ 选书操作: 需要优化 (> 100ms)")

    if qc_time < 0.1:
        print("  ✓ 质检操作: 优秀 (< 100ms)")
    elif qc_time < 1.0:
        print("  ⚠ 质检操作: 良好 (100ms-1秒)")
    else:
        print("  ✗ 质检操作: 需要优化 (> 1秒)")

    print("\n✅ 基准测试完成！")

    return {
        'init': init_time,
        'select': select_time,
        'stats': stats_time,
        'qc': qc_time,
        'template': template_time
    }


def main():
    parser = argparse.ArgumentParser(description="Read Book Skill 性能基准测试")
    parser.add_argument("--iterations", type=int, default=5, help="迭代次数（默认5）")
    parser.add_argument("--json", action="store_true", help="输出JSON格式")

    args = parser.parse_args()

    results = run_benchmark(args.iterations)

    if args.json:
        import json
        print("\n📄 JSON格式结果:")
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
