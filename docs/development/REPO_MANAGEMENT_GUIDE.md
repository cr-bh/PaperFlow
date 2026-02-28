# 双仓库管理指南

> **版本**: 1.0
> **创建日期**: 2026-02-28
> **最后更新**: 2026-02-28
> **状态**: 已发布

---

## 📋 概述

PaperBrain 采用**双仓库 + 双分支**架构，实现私有开发与开源发布的隔离。

| 仓库 | 可见性 | Remote 名称 | 分支 | 地址 |
|------|--------|------------|------|------|
| `cr-bh/Paper-Brain` | **Private** | `origin` | `main-private` | https://github.com/cr-bh/Paper-Brain |
| `cr-bh/PaperBrain` | **Public** | `public` | `main` | https://github.com/cr-bh/PaperBrain |

---

## 🔄 日常开发流程

所有日常开发都在 `main-private` 分支上进行，推送到私有仓库。

```bash
# 确认在 main-private 分支
git checkout main-private

# 正常开发、提交
git add .
git commit -m "feat: 你的提交信息"

# 推送到私有仓库
git push origin main-private
```

---

## 🚀 发布到开源仓库

当功能稳定、准备对外发布时，将代码同步到公开仓库。

```bash
# 1. 切换到 main 分支
git checkout main

# 2. 合并 main-private 的更新
git merge main-private

# 3. 推送到公开仓库
git push public main

# 4. 切回 main-private 继续开发
git checkout main-private
```

### 一行命令版本

```bash
git checkout main && git merge main-private && git push public main && git checkout main-private
```

---

## ⚠️ 重要注意事项

### 1. 绝对不要做的事

| 禁止操作 | 原因 |
|---------|------|
| `git push origin main` | 不要把 main 推到私有仓库（保持 origin 只有 main-private） |
| `git push public main-private` | 不要把 main-private 推到公开仓库 |
| 在 `main` 上直接开发 | main 仅用于发布，所有开发在 main-private 上 |
| 提交 `.env` 文件 | 包含你的 API 密钥（已被 `.gitignore` 保护） |
| 提交 `data/api_config.json` | 包含 API Key（已被 `data/*.json` 规则保护） |

### 2. 不影响你的 API 配置的原因

- `.env` 在 `.gitignore` 中 → 从不被提交，切换分支也不会丢失
- `.env.example` 是模板文件 → 应用程序读取的是 `.env`，不是 `.env.example`
- `data/api_config.json` 在 `.gitignore` 中 → 从不被提交
- `config.py` 第 10 行: `env_path = Path(__file__).parent / '.env'` → 只读 `.env`

### 3. 关于 `.env` vs `.env.example`

| 文件 | 用途 | 是否提交 | 应用是否读取 |
|------|------|---------|------------|
| `.env` | **你的真实配置** | ❌ 不提交 | ✅ 读取 |
| `.env.example` | 给开源用户的模板 | ✅ 提交 | ❌ 不读取 |

---

## 🔍 常用检查命令

```bash
# 查看当前分支
git branch

# 查看所有 remote
git remote -v

# 查看 main-private 比 main 多了哪些 commit
git log main..main-private --oneline

# 查看 main 和 main-private 的文件差异
git diff main main-private --stat
```

---

## 🛠️ 故障排查

### 场景 1: 不小心在 main 上提交了代码

```bash
# 记下 commit hash
git log --oneline -3

# 切到 main-private，cherry-pick 这个 commit
git checkout main-private
git cherry-pick <commit-hash>

# 回到 main，回退
git checkout main
git reset --hard HEAD~1
```

### 场景 2: main 和 main-private 出现冲突

```bash
git checkout main
git merge main-private
# 手动解决冲突
git add .
git commit -m "merge: 解决合并冲突"
git push public main
git checkout main-private
```

### 场景 3: 想查看公开仓库当前状态

```bash
git log public/main --oneline -10
```

### 场景 4: 想让某些文件只存在于 main-private

只要这些文件不提交到 `main` 分支即可。有两种方式：

**方式 A**: 文件不跟踪（放在 `.gitignore` 中或不 `git add`）

**方式 B**: 使用选择性合并
```bash
git checkout main
git merge main-private --no-commit
# 移除不想公开的文件
git reset HEAD <private-file>
git checkout -- <private-file>
git commit -m "merge: 同步 main-private（排除私有文件）"
```

---

## 📐 架构示意

```
本地工作区 (一份代码)
│
├── .env                    ← 你的真实 API 配置（不提交）
├── data/api_config.json    ← 设置页面保存的配置（不提交）
├── .env.example            ← 开源用户模板（提交）
│
├── [origin] cr-bh/Paper-Brain (Private)
│   └── main-private ← 日常开发推送到这里
│
└── [public] cr-bh/PaperBrain (Public)
    └── main ← 发版时推送到这里
```
