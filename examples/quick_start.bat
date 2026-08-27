@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo 🚀 Read Book Skill 5分钟快速开始
echo ================================
echo.

:: 检查Python
echo [1/8] 检查Python版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python版本: %PYTHON_VERSION%
echo.

:: 创建项目
echo [2/8] 创建读书项目...
python scripts/init_project.py ./my-book-project
if errorlevel 1 (
    echo ❌ 项目创建失败
    pause
    exit /b 1
)
echo ✓ 项目创建成功
echo.

:: 进入项目
cd my-book-project

:: 添加书籍
echo [3/8] 添加《底层逻辑》到书单...
python scripts/book_manager.py add "底层逻辑" --author "刘润" --priority "高" --tags "思维方法,认知科学,商业"
if errorlevel 1 (
    echo ❌ 书籍添加失败
    pause
    exit /b 1
)
echo ✓ 书籍添加成功
echo.

:: 查看书单
echo [4/8] 查看书单统计...
python scripts/book_manager.py stats
echo ✓ 书单查看成功
echo.

:: 选书
echo [5/8] 选择《底层逻辑》...
python scripts/book_manager.py select --title "底层逻辑"
echo ✓ 选书成功
echo.

:: 生成HTML骨架
echo [6/8] 生成HTML精读笔记骨架...
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set TODAY=%%a%%b%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set NOW=%%a%%b
set TASK_ID=demo_%TODAY%_%NOW%
python scripts/html_template.py generate --title "底层逻辑" --author "刘润" --task-id %TASK_ID% --tags "思维方法,认知科学,商业" --priority "高"
if errorlevel 1 (
    echo ❌ HTML骨架生成失败
    pause
    exit /b 1
)
echo ✓ HTML骨架生成成功
echo.

:: 查看生成的文件
echo [7/8] 查看生成的文件...
dir book_cache\book_raw_content\
echo ✓ 文件列表查看成功
echo.

:: 完成提示
echo [8/8] 🎉 快速开始完成！
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✅ 你已经成功:
echo   1. 创建了一个读书项目
echo   2. 添加了《底层逻辑》到书单
echo   3. 生成了HTML精读笔记骨架
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📋 下一步操作:
echo.
echo 1. 用浏览器打开生成的HTML文件，查看骨架模板
echo    文件位置: book_cache\book_raw_content\demo_*.html
echo.
echo 2. 使用AI（如Claude）填充精读内容:
echo    - 告诉AI: "帮我读一本《底层逻辑》"
echo    - AI会自动执行完整的7步流水线
echo    - 生成15000+字的深度精读笔记
echo.
echo 3. 质检精读笔记:
echo    python scripts\qc_check.py book_cache\book_raw_content\demo_*.html
echo.
echo 4. 更新阅读状态:
echo    python scripts\book_manager.py update "底层逻辑"
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📖 更多信息:
echo   - README.md          项目说明
echo   - GETTING_STARTED.md 快速开始指南
echo   - FAQ.md             常见问题
echo   - examples\          示例文件
echo.
echo 🎯 祝你阅读愉快！
echo.

pause
