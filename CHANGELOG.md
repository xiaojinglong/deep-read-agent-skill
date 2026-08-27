# Changelog

本文件记录 Read Book Skill 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- 初始版本发布
- 完整的读书智能体功能
- 书单管理（添加、删除、搜索、统计）
- HTML精读笔记生成（15模块，15000+字）
- 自动质检（11项检查）
- 项目初始化脚本
- 完整的单元测试
- 详细的文档和使用指南

### Changed
- 无

### Deprecated
- 无

### Removed
- 无

### Fixed
- 无

### Security
- 无

## [5.0.0] - 2026-08-27

### Added
- 🎨 **HTML模板v5版本**
  - 暖色调精致配色系统
  - 15模块emoji标题体系
  - 场景→步骤→心法格式
  - 一页精华复盘块
  - 5种CSS可视化图表（条形图、时间线、思维导图、流程图、雷达图）
  - 响应式设计（支持移动端）

- 📚 **书单管理增强**
  - 支持10本示例书籍
  - JSON格式统一输出
  - 错误处理优化
  - 支持--project-dir参数

- ✅ **质检系统升级**
  - 11项质量检查
  - 模块内容实质检查（每模块≥200字）
  - 图表有效性检查（≥80字内容）
  - 重复注水检测
  - 支持--json格式输出

- 🧪 **测试覆盖**
  - 33个单元测试
  - 书单管理测试（16个）
  - 质检脚本测试（17个）
  - 测试运行脚本

- 📖 **文档完善**
  - 详细的README.md
  - 贡献指南（CONTRIBUTING.md）
  - 版本更新日志（CHANGELOG.md）
  - MIT许可证
  - .gitignore配置

### Changed
- 🔄 **代码优化**
  - load_books() 添加错误处理
  - to_slug() 函数实现
  - 输出格式统一为JSON
  - 模块查找逻辑优化（避免误匹配）

- 📝 **文档同步**
  - 字数限制统一为15000字
  - 模块数量统一为15个
  - 所有文档保持一致

### Fixed
- 🐛 **Bug修复**
  - 随机选书未过滤已读问题
  - qc_check.py --project-dir参数支持
  - init_project.py复制references和assets目录
  - GITIGNORE字符串未正确关闭

## [4.0.0] - 2026-08-20

### Added
- 初始版本框架
- 基础书单管理功能
- HTML模板v4版本
- 基础质检功能

### Changed
- 无

### Fixed
- 无

---

## 版本说明

### 版本号含义

- **MAJOR (主版本号)**: 不兼容的API修改
- **MINOR (次版本号)**: 向后兼容的功能性新增
- **PATCH (修订号)**: 向后兼容的问题修正

### 变更类型

- **Added**: 新功能
- **Changed**: 对现有功能的变更
- **Deprecated**: 已经不建议使用，即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: Bug修复
- **Security**: 安全相关的变更

### 链接

- GitHub Releases
- 完整变更历史

---

**感谢所有为这个项目做出贡献的人！** 🙏
