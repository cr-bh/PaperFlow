# API 隐私保护方案（已废弃）

> **状态**: ⚠️ 已废弃
> **废弃日期**: 2026-02-28
> **替代文档**: [双仓库管理指南](REPO_MANAGEMENT_GUIDE.md)

---

## 说明

本文档描述的是旧方案（同一仓库内使用 `main` / `main-private` 两个分支管理公开与私有代码）。

该方案已被**双仓库方案**取代：

| 仓库 | 可见性 | 分支 | 用途 |
|------|--------|------|------|
| `cr-bh/Paper-Brain` | Private | `main-private` | 日常开发 |
| `cr-bh/PaperBrain` | Public | `main` | 开源发布 |

请参阅 [双仓库管理指南](REPO_MANAGEMENT_GUIDE.md) 了解完整的操作流程。
