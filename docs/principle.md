# PaperBrain 文档管理规范

> **版本**: 1.0
> **创建日期**: 2026-02-14
> **最后更新**: 2026-02-14

---

## 📋 目录结构

所有文档统一存放在 `docs/` 目录下，按以下分类组织：

```
docs/
├── principle.md                    # 本文档管理规范（必读）
├── README.md                       # 文档目录索引
│
├── guides/                         # 用户指南
│   ├── AUTO_SCHOLAR_GUIDE.md      # Auto-Scholar 使用指南
│   ├── CONFIGURATION.md           # 配置指南
│   └── ...
│
├── technical/                      # 技术文档
│   ├── TECHNICAL_DOCUMENTATION.md # 完整技术文档
│   ├── PRD.md                     # 产品需求文档
│   └── ...
│
├── changelogs/                     # 版本更新日志
│   ├── CHANGELOG.md               # 主更新日志（汇总）
│   ├── v1.4.0/                    # v1.4.0 版本文档
│   │   ├── UPDATE_LOG.md          # 更新日志
│   │   ├── KNOWN_ISSUES.md        # 已知问题
│   │   └── DEBUG_LOG.md           # 调试日志
│   ├── v1.3.1/                    # v1.3.1 版本文档
│   │   └── UPDATE_LOG.md
│   ├── v1.3.0/                    # v1.3.0 版本文档
│   │   └── UPDATE_LOG.md
│   └── ...
│
├── features/                       # 功能说明文档
│   ├── VENUE_INSTITUTION.md       # 顶会机构识别功能
│   ├── IMPORT_FEATURE.md          # 论文导入功能
│   └── ...
│
├── development/                    # 开发文档
│   ├── iteration_logs/            # 迭代日志
│   │   ├── 2026-02-13.md
│   │   └── ...
│   ├── bugfix_logs/               # Bug 修复日志
│   │   ├── 2026-02-12.md
│   │   └── ...
│   └── plans/                     # 开发计划
│       └── ...
│
└── archive/                        # 归档文档（过期/废弃）
    └── ...
```

---

## 📝 文档分类规则

### 1. 用户指南 (`guides/`)

**用途**: 面向最终用户的使用说明文档

**命名规范**: `<功能名>_GUIDE.md`

**内容要求**:
- 功能概述
- 快速开始
- 详细使用步骤
- 常见问题
- 示例截图

**示例**:
- `AUTO_SCHOLAR_GUIDE.md` - Auto-Scholar 使用指南
- `CONFIGURATION.md` - 配置指南
- `TAG_MANAGEMENT_GUIDE.md` - 标签管理指南

---

### 2. 技术文档 (`technical/`)

**用途**: 面向开发者的技术架构和 API 文档

**命名规范**: `<文档类型>.md`

**内容要求**:
- 系统架构
- 数据模型
- API 接口
- 技术选型
- 最佳实践

**示例**:
- `TECHNICAL_DOCUMENTATION.md` - 完整技术文档
- `PRD.md` - 产品需求文档
- `API_REFERENCE.md` - API 参考文档

---

### 3. 版本更新日志 (`changelogs/`)

**用途**: 记录每个版本的变更历史

**目录结构**:
```
changelogs/
├── CHANGELOG.md           # 主更新日志（所有版本汇总）
└── v<版本号>/             # 每个版本一个文件夹
    ├── UPDATE_LOG.md      # 详细更新日志
    ├── KNOWN_ISSUES.md    # 已知问题（可选）
    └── DEBUG_LOG.md       # 调试日志（可选）
```

**命名规范**:
- 版本文件夹: `v<major>.<minor>.<patch>/` (如 `v1.4.0/`)
- 更新日志: `UPDATE_LOG.md`
- 已知问题: `KNOWN_ISSUES.md`
- 调试日志: `DEBUG_LOG.md`

**CHANGELOG.md 格式**:
```markdown
# 更新日志 (CHANGELOG)

## [v1.4.0] - 2026-02-13

### ✨ 新增功能
- 功能1
- 功能2

### 🐛 Bug 修复
- 修复1
- 修复2

### 🚀 性能优化
- 优化1

### 📚 文档更新
- 文档1

详细内容请参考 [v1.4.0 更新日志](changelogs/v1.4.0/UPDATE_LOG.md)

---

## [v1.3.1] - 2026-02-13
...
```

**UPDATE_LOG.md 格式**:
```markdown
# 更新日志 v1.4.0

## 📅 更新日期
2026-02-13

## 🎯 更新概述
简要描述本次更新的主要内容

## ✨ 新增功能

### 1. 功能名称
详细描述...

## 🐛 Bug 修复

### 1. 问题描述
详细描述...

## 🏗️ 技术架构

### 新增文件
- `file1.py` - 说明
- `file2.py` - 说明

### 修改文件
- `file3.py` - 说明

## 📝 使用说明
...

## ⚠️ 注意事项
...
```

---

### 4. 功能说明文档 (`features/`)

**用途**: 详细说明特定功能的设计和实现

**命名规范**: `<功能名>.md`

**内容要求**:
- 功能概述
- 实现原理
- 数据流程
- 技术实现
- 使用示例
- 配置说明

**示例**:
- `VENUE_INSTITUTION.md` - 顶会机构识别功能
- `IMPORT_FEATURE.md` - 论文导入功能
- `RAG_QA.md` - RAG 问答功能

---

### 5. 开发文档 (`development/`)

**用途**: 记录开发过程中的迭代、Bug 修复、计划等

**子目录**:

#### 5.1 迭代日志 (`iteration_logs/`)
**命名规范**: `YYYY-MM-DD.md`

**内容要求**:
- 日期和版本
- 开发任务列表
- 遇到的问题
- 解决方案
- 代码变更

#### 5.2 Bug 修复日志 (`bugfix_logs/`)
**命名规范**: `YYYY-MM-DD.md` 或 `<bug描述>.md`

**内容要求**:
- Bug 描述
- 复现步骤
- 根本原因
- 解决方案
- 测试验证

#### 5.3 开发计划 (`plans/`)
**命名规范**: `<功能名>_PLAN.md`

**内容要求**:
- 功能需求
- 技术方案
- 实现步骤
- 时间规划
- 风险评估

---

### 6. 归档文档 (`archive/`)

**用途**: 存放过期或废弃的文档

**规则**:
- 当文档不再适用当前版本时，移动到此目录
- 保留原文件名，添加归档日期前缀: `ARCHIVED_YYYY-MM-DD_<原文件名>.md`
- 在原位置添加说明文件，指向新文档

---

## 🔄 文档更新流程

### 新增功能时

1. **开发阶段**:
   - 在 `development/plans/` 创建功能计划文档
   - 在 `development/iteration_logs/` 记录开发过程

2. **功能完成后**:
   - 在 `features/` 创建功能说明文档
   - 在 `guides/` 更新或创建用户指南
   - 更新 `technical/TECHNICAL_DOCUMENTATION.md`

3. **版本发布时**:
   - 在 `changelogs/v<版本号>/` 创建版本文档
   - 更新 `changelogs/CHANGELOG.md` 主日志
   - 更新根目录 `README.md`

### Bug 修复时

1. **修复过程**:
   - 在 `development/bugfix_logs/` 记录 Bug 详情和修复过程

2. **版本发布时**:
   - 在 `changelogs/v<版本号>/UPDATE_LOG.md` 中添加 Bug 修复说明
   - 更新 `changelogs/CHANGELOG.md`

### 文档更新时

1. **小改动**: 直接修改对应文档，更新文档头部的"最后更新"日期
2. **大改动**:
   - 将旧版本移动到 `archive/`
   - 创建新版本文档
   - 在 `changelogs/` 中记录文档变更

---

## 📐 文档编写规范

### 文档头部

每个文档都应包含以下头部信息：

```markdown
# 文档标题

> **版本**: 1.0
> **创建日期**: YYYY-MM-DD
> **最后更新**: YYYY-MM-DD
> **作者**: 作者名
> **状态**: 草稿 / 审核中 / 已发布 / 已归档

---
```

### Markdown 格式规范

1. **标题层级**:
   - `#` 一级标题（文档标题，每个文档只有一个）
   - `##` 二级标题（主要章节）
   - `###` 三级标题（子章节）
   - `####` 四级标题（详细说明）

2. **代码块**:
   - 使用三个反引号包裹
   - 指定语言类型: ```python, ```bash, ```json

3. **列表**:
   - 无序列表使用 `-`
   - 有序列表使用 `1.`, `2.`, `3.`
   - 嵌套列表使用 2 个空格缩进

4. **强调**:
   - 粗体: `**文本**`
   - 斜体: `*文本*`
   - 代码: `` `代码` ``

5. **链接**:
   - 内部链接: `[文档名](../path/to/doc.md)`
   - 外部链接: `[链接文本](https://example.com)`

6. **表格**:
   ```markdown
   | 列1 | 列2 | 列3 |
   |-----|-----|-----|
   | 值1 | 值2 | 值3 |
   ```

7. **Emoji 使用**:
   - ✨ 新增功能
   - 🐛 Bug 修复
   - 🚀 性能优化
   - 📚 文档更新
   - ⚠️ 注意事项
   - 📋 列表/目录
   - 🔧 配置
   - 💡 提示
   - ❓ 问题

---

## 🔍 文档审查清单

在提交文档前，请确认：

- [ ] 文档头部信息完整
- [ ] 标题层级正确
- [ ] 代码块有语言标识
- [ ] 链接可用
- [ ] 图片路径正确
- [ ] 拼写检查通过
- [ ] 格式统一
- [ ] 内容准确
- [ ] 示例可运行
- [ ] 已更新相关索引

---

## 📚 文档索引维护

### docs/README.md

在 `docs/README.md` 中维护所有文档的索引：

```markdown
# PaperBrain 文档中心

## 📖 用户指南
- [Auto-Scholar 使用指南](guides/AUTO_SCHOLAR_GUIDE.md)
- [配置指南](guides/CONFIGURATION.md)

## 🔧 技术文档
- [技术文档](technical/TECHNICAL_DOCUMENTATION.md)
- [产品需求文档](technical/PRD.md)

## 📝 更新日志
- [主更新日志](changelogs/CHANGELOG.md)
- [v1.4.0 更新日志](changelogs/v1.4.0/UPDATE_LOG.md)

## 🎯 功能说明
- [顶会机构识别](features/VENUE_INSTITUTION.md)
- [论文导入功能](features/IMPORT_FEATURE.md)

## 🛠️ 开发文档
- [迭代日志](development/iteration_logs/)
- [Bug 修复日志](development/bugfix_logs/)
```

---

## 🚀 迁移现有文档

### 迁移步骤

1. **创建新目录结构**:
   ```bash
   mkdir -p docs/{guides,technical,changelogs,features,development/{iteration_logs,bugfix_logs,plans},archive}
   ```

2. **移动文件**:
   - 用户指南 → `guides/`
   - 技术文档 → `technical/`
   - 版本日志 → `changelogs/v<版本号>/`
   - 功能说明 → `features/`
   - 开发日志 → `development/`

3. **更新链接**:
   - 更新所有文档中的相对路径
   - 更新 README.md 中的链接

4. **创建索引**:
   - 创建 `docs/README.md`
   - 更新根目录 `README.md`

---

## 📌 注意事项

1. **文档命名**:
   - 使用英文命名
   - 使用大写字母和下划线
   - 避免特殊字符

2. **版本号规范**:
   - 遵循语义化版本 (Semantic Versioning)
   - 格式: `v<major>.<minor>.<patch>`
   - 示例: `v1.4.0`, `v1.3.1`

3. **文档语言**:
   - 技术文档优先使用中文
   - 代码注释使用英文
   - 用户指南提供中英文版本

4. **图片管理**:
   - 图片存放在 `docs/images/` 目录
   - 按功能或版本分类: `docs/images/v1.4.0/`, `docs/images/auto-scholar/`
   - 使用相对路径引用

5. **定期维护**:
   - 每个版本发布后更新文档
   - 每季度审查文档准确性
   - 及时归档过期文档

---

## 📞 联系方式

如有文档相关问题，请：
- 提交 Issue
- 联系项目维护者
- 参考本规范文档

---

**最后更新**: 2026-02-14
**维护者**: PaperBrain Team
