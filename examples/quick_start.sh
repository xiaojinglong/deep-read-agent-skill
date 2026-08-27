#!/bin/bash
# Read Book Skill 5分钟快速开始
# 用法: bash examples/quick_start.sh

set -e

echo "🚀 Read Book Skill 5分钟快速开始"
echo "================================"
echo ""

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查Python版本
echo -e "${BLUE}[1/8] 检查Python版本...${NC}"
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ 错误: 未找到Python，请先安装Python 3.7+${NC}"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python版本: $PYTHON_VERSION${NC}"
echo ""

# 创建项目
echo -e "${BLUE}[2/8] 创建读书项目...${NC}"
$PYTHON_CMD scripts/init_project.py ./my-book-project
echo -e "${GREEN}✓ 项目创建成功${NC}"
echo ""

# 进入项目
cd my-book-project

# 添加书籍
echo -e "${BLUE}[3/8] 添加《底层逻辑》到书单...${NC}"
$PYTHON_CMD scripts/book_manager.py add "底层逻辑" \
  --author "刘润" \
  --priority "高" \
  --tags "思维方法,认知科学,商业"
echo -e "${GREEN}✓ 书籍添加成功${NC}"
echo ""

# 查看书单
echo -e "${BLUE}[4/8] 查看书单统计...${NC}"
$PYTHON_CMD scripts/book_manager.py stats
echo -e "${GREEN}✓ 书单查看成功${NC}"
echo ""

# 选书
echo -e "${BLUE}[5/8] 选择《底层逻辑》...${NC}"
$PYTHON_CMD scripts/book_manager.py select --title "底层逻辑"
echo -e "${GREEN}✓ 选书成功${NC}"
echo ""

# 生成HTML骨架
echo -e "${BLUE}[6/8] 生成HTML精读笔记骨架...${NC}"
$PYTHON_CMD scripts/html_template.py generate \
  --title "底层逻辑" \
  --author "刘润" \
  --task-id demo_$(date +%Y%m%d_%H%M%S) \
  --tags "思维方法,认知科学,商业" \
  --priority "高"
echo -e "${GREEN}✓ HTML骨架生成成功${NC}"
echo ""

# 查看生成的文件
echo -e "${BLUE}[7/8] 查看生成的文件...${NC}"
ls -la book_cache/book_raw_content/
echo -e "${GREEN}✓ 文件列表查看成功${NC}"
echo ""

# 完成提示
echo -e "${YELLOW}[8/8] 🎉 快速开始完成！${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ 你已经成功:${NC}"
echo "  1. 创建了一个读书项目"
echo "  2. 添加了《底层逻辑》到书单"
echo "  3. 生成了HTML精读笔记骨架"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}📋 下一步操作:${NC}"
echo ""
echo "1. 用浏览器打开生成的HTML文件，查看骨架模板"
echo "   文件位置: book_cache/book_raw_content/demo_*.html"
echo ""
echo "2. 使用AI（如Claude）填充精读内容:"
echo "   - 告诉AI: '帮我读一本《底层逻辑》'"
echo "   - AI会自动执行完整的7步流水线"
echo "   - 生成15000+字的深度精读笔记"
echo ""
echo "3. 质检精读笔记:"
echo "   python scripts/qc_check.py book_cache/book_raw_content/demo_*.html"
echo ""
echo "4. 更新阅读状态:"
echo "   python scripts/book_manager.py update \"底层逻辑\""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}📖 更多信息:${NC}"
echo "  - README.md          项目说明"
echo "  - GETTING_STARTED.md 快速开始指南"
echo "  - FAQ.md             常见问题"
echo "  - examples/          示例文件"
echo ""
echo -e "${GREEN}🎯 祝你阅读愉快！${NC}"
