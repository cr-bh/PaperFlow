# API 隐私保护方案

本文档说明如何管理包含公司 API 的私密分支和公开分支。

---

## 📋 分支策略

### 分支说明

- **`main-private`**: 私密分支，包含真实的公司 API 配置
- **`main`**: 公开分支，API 配置已脱敏，可以公开到 GitHub

---

## 🔧 初始设置

### 1. 创建私密分支

```bash
# 当前在 main 分支
git checkout -b main-private

# 推送私密分支到远程（如果需要备份）
git push origin main-private
```

### 2. 在 main 分支脱敏 API 配置

```bash
# 切换回 main 分支
git checkout main

# 编辑 .env.example，替换公司 API 为占位符
# 见下方"脱敏配置"部分
```

---

## 🔒 脱敏配置

### .env.example 脱敏版本

将 `.env.example` 中的公司 API 地址替换为通用占位符：

```bash
# Gemini API Configuration (用于论文分析)
GEMINI_API_KEY=your_gemini_api_key_here
LLM_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent
LLM_BEARER_TOKEN=your_bearer_token_here

# Doubao API Configuration (专用于 Auto-Scholar 评分)
DOUBAO_API_URL=https://ark.cn-beijing.volces.com/api/v3/chat/completions
DOUBAO_BEARER_TOKEN=your_doubao_bearer_token_here

# 其他配置保持不变...
```

### README.md 更新

在 README 中说明支持的 API：

```markdown
### LLM API 配置

PaperBrain 支持以下 LLM API：

- **Gemini API**: Google 官方 API
- **豆包 API**: 字节跳动火山引擎 API
- **自定义 API**: 任何兼容 OpenAI 格式的 API

配置方法请参考 [配置指南](docs/guides/CONFIGURATION.md)
```

---

## 🔄 日常工作流程

### 在私密分支开发

```bash
# 切换到私密分支
git checkout main-private

# 正常开发和提交
git add .
git commit -m "feat: add new feature"

# 推送到私密分支（可选，用于备份）
git push origin main-private
```

### 同步到公开分支

```bash
# 1. 确保私密分支是最新的
git checkout main-private
git add .
git commit -m "your commit message"

# 2. 切换到公开分支
git checkout main

# 3. 合并私密分支的代码（不包括 .env 相关文件）
git merge main-private --no-commit

# 4. 检查并恢复 .env.example 为脱敏版本
git checkout HEAD -- .env.example

# 5. 检查是否有其他需要脱敏的文件
git status
git diff

# 6. 提交并推送到公开仓库
git commit -m "sync: merge from private branch"
git push origin main
```

---

## 🛡️ 安全检查清单

在推送到公开分支前，请确认：

- [ ] `.env.example` 中的 API 地址已脱敏
- [ ] `.env` 文件在 `.gitignore` 中（不会被提交）
- [ ] 代码中没有硬编码的 API Key 或 Token
- [ ] 文档中没有提及公司内部 API 地址
- [ ] 截图中没有显示真实的 API 配置

---

## 📝 .gitignore 配置

确保 `.gitignore` 包含以下内容：

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# API keys and secrets
*_secret.py
*_private.py
secrets/
```

---

## 🔍 查找敏感信息

使用以下命令查找可能的敏感信息：

```bash
# 查找 sankuai.com 域名
git grep -i "sankuai.com"

# 查找可能的 API Key
git grep -i "api.*key"
git grep -i "bearer.*token"

# 查找 .env 文件引用
git grep -i "\.env"
```

---

## 🚨 紧急处理：已提交敏感信息

如果不小心将敏感信息提交到公开分支：

### 方法 1: 修改最近的提交

```bash
# 如果是最近一次提交
git reset --soft HEAD~1
# 修改文件，移除敏感信息
git add .
git commit -m "fix: remove sensitive info"
git push origin main --force
```

### 方法 2: 使用 git filter-branch（彻底清除历史）

```bash
# 从所有历史中移除敏感文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive/file" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin main --force --all
```

### 方法 3: 使用 BFG Repo-Cleaner（推荐）

```bash
# 安装 BFG
brew install bfg  # macOS

# 清除敏感信息
bfg --replace-text passwords.txt  # 替换文本
bfg --delete-files sensitive.env  # 删除文件

# 清理和推送
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin main --force
```

---

## 📚 相关文档

- [Git 分支管理最佳实践](https://git-scm.com/book/zh/v2)
- [保护敏感数据](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure)
- [.gitignore 模板](https://github.com/github/gitignore)

---

## 💡 最佳实践

1. **永远不要提交 .env 文件**
2. **定期检查公开分支的敏感信息**
3. **使用环境变量管理所有敏感配置**
4. **在 README 中提供通用的配置示例**
5. **为团队成员提供私密分支访问权限**

---

**最后更新**: 2026-02-14
**维护者**: PaperBrain Team
