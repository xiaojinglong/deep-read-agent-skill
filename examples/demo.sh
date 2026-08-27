#!/bin/bash
# Read Book Skill 快速演示脚本
# 用法: bash examples/demo.sh

set -e  # 遇到错误立即退出

echo "📚 Read Book Skill 快速演示"
echo "=========================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 创建演示项目
echo -e "${BLUE}[1/6] 创建演示项目...${NC}"
python scripts/init_project.py ./demo-project
echo -e "${GREEN}✓ 演示项目创建成功${NC}"
echo ""

# 2. 进入项目目录
cd demo-project

# 3. 查看书单统计
echo -e "${BLUE}[2/6] 查看书单统计...${NC}"
python scripts/book_manager.py stats
echo -e "${GREEN}✓ 书单统计查看成功${NC}"
echo ""

# 4. 选一本书
echo -e "${BLUE}[3/6] 选择一本书...${NC}"
python scripts/book_manager.py select
echo -e "${GREEN}✓ 选书成功${NC}"
echo ""

# 5. 生成HTML骨架
echo -e "${BLUE}[4/6] 生成HTML骨架...${NC}"
python scripts/html_template.py generate \
  --title "穷查理宝典" \
  --author "查理·芒格" \
  --task-id demo_20260827 \
  --tags "投资,思维模型" \
  --priority "高"
echo -e "${GREEN}✓ HTML骨架生成成功${NC}"
echo ""

# 6. 查看生成的文件
echo -e "${BLUE}[5/6] 查看生成的文件...${NC}"
ls -la book_cache/book_raw_content/
echo -e "${GREEN}✓ 文件列表查看成功${NC}"
echo ""

# 7. 提示下一步
echo -e "${YELLOW}[6/6] 下一步操作:${NC}"
echo ""
echo "1. 用浏览器打开生成的HTML文件:"
echo "   book_cache/book_raw_content/demo_20260827.html"
echo ""
echo "2. 使用AI（如Claude）填充内容:"
echo "   - 读取骨架文件"
echo "   - 按15个模块填充内容"
echo "   - 目标15000+字"
echo ""
echo "3. 质检:"
echo "   python scripts/qc_check.py book_cache/book_raw_content/demo_20260827.html"
echo ""
echo "4. 更新阅读状态:"
echo "   python scripts/book_manager.py update \"穷查理宝典\""
echo ""
echo -e "${GREEN}🎉 演示完成！${NC}"
echo ""
echo "📖 完整文档: README.md"
echo "🚀 快速开始: GETTING_STARTED.md"
echo "❓ 常见问题: FAQ.md"
