# API 设置与配置管理

> **版本**: 1.0
> **创建日期**: 2026-02-28
> **最后更新**: 2026-02-28
> **状态**: 已发布

---

## 📋 功能概述

PaperBrain 的 API 设置功能提供了图形化的 LLM API 配置界面，支持两种接入方式：

- **标准模式**: 从预设提供商列表中选择（DeepSeek、通义千问、OpenAI 等），只需填写 API Key
- **自定义模式**: 手动配置 API 地址、Token、格式等，适配内部部署或非标准 API

系统支持配置两个独立的 LLM 角色：
- **主 LLM**: 负责论文总结、思维导图生成、标签生成、RAG 问答
- **评分 LLM**: 负责 Auto-Scholar 论文评分和 PDF 元数据提取（默认复用主 LLM）

---

## 🔧 实现原理

### 配置层级

```
┌─────────────────────────┐
│  data/api_config.json   │  ← 设置页面保存（最高优先级）
│  (JSON 文件持久化)       │
└──────────┬──────────────┘
           │ 不存在时
           ▼
┌─────────────────────────┐
│  .env 环境变量           │  ← 传统配置方式
│  LLM_API_URL / TOKEN    │
└──────────┬──────────────┘
           │ 不存在时
           ▼
┌─────────────────────────┐
│  默认空配置              │  ← 未配置状态
│  (可启动，不可调用 API)   │
└─────────────────────────┘
```

### 双模式设计

#### 标准模式 (Standard Mode)

面向使用公共 API 服务的用户：

```python
{
    "mode": "standard",
    "provider": "deepseek",       # 提供商标识
    "api_key": "sk-xxx",          # API Key
    "model": "deepseek-chat",     # 模型名称
    "temperature": 0.7,
    "max_tokens": 8192
}
```

系统根据 `provider` 自动获取对应的 Base URL 和可选模型列表。

#### 自定义模式 (Custom Mode)

面向使用内部部署 API 或非标准接口的用户：

```python
{
    "mode": "custom",
    "api_url": "https://internal.company.com/api/v1",
    "api_token": "Bearer xxx",
    "api_format": "gemini",       # "openai" 或 "gemini"
    "model": "gemini-2.0-flash",
    "custom_ssl": True,           # 降低 SSL 安全等级
    "temperature": 0.7,
    "max_tokens": 8192
}
```

### API 格式支持

| 格式 | 请求方式 | 认证方式 | 典型用户 |
|------|---------|---------|---------|
| **OpenAI 兼容** | `POST /chat/completions` | `Authorization: Bearer <key>` | DeepSeek、Qwen、OpenAI、Moonshot、GLM、SiliconFlow |
| **Gemini** | `POST :generateContent` | `Authorization: Bearer <token>` | Google Gemini、内部部署的 Gemini 格式 API |

---

## 📊 数据流程

### 配置保存流程

```
用户在设置页面修改配置
    ↓
点击「保存配置」
    ↓
save_config() → 写入 data/api_config.json
    ↓
llm_service.reload() → 重新加载配置
doubao_service.reload() → 重新加载配置
    ↓
配置立即生效，无需重启
```

### API 调用流程

```
业务层调用 llm_service.generate_text(prompt)
    ↓
_ensure_configured() → 检查 API 是否已配置
    ↓
_call_api() → 根据 api_format 分发
    ├─ _call_openai_api() → OpenAI 格式请求
    └─ _call_gemini_api() → Gemini 格式请求
    ↓
返回生成文本
```

---

## 🛠️ 技术实现

### 核心模块

#### `services/api_config.py`

| 函数/常量 | 说明 |
|-----------|------|
| `PROVIDERS` | 预设提供商字典（名称、Base URL、模型列表、文档链接） |
| `DEFAULT_CONFIG` | 默认配置模板（main_llm + scoring_llm） |
| `detect_api_format(url)` | 从 URL 关键词自动检测 API 格式 |
| `load_config()` | 加载配置（JSON → .env → 默认） |
| `save_config(cfg)` | 保存配置到 JSON 文件 |
| `get_effective_api_params(role)` | 获取指定角色的有效 API 参数 |
| `is_role_configured(role)` | 检查指定角色是否已配置 |

#### `services/llm_service.py`

| 方法 | 说明 |
|------|------|
| `__init__(role)` | 初始化服务，加载指定角色配置 |
| `_load_config()` | 从 api_config 加载配置参数 |
| `reload()` | 运行时重新加载配置 |
| `is_configured()` | 检查 API 是否可用 |
| `_call_openai_api()` | OpenAI 格式 API 调用 |
| `_call_gemini_api()` | Gemini 格式 API 调用 |
| `test_connection()` | 测试 API 连接 |
| `generate_text(prompt)` | 生成文本（自动选择格式） |
| `generate_json(prompt)` | 生成 JSON 格式的文本 |

#### `ui/settings.py`

| 函数 | 说明 |
|------|------|
| `show_settings()` | 设置页面主入口 |
| `_render_llm_config(role, label, cfg)` | 渲染 LLM 配置区域 |
| `_render_standard_mode(role, cfg)` | 标准模式 UI |
| `_render_custom_mode(role, cfg)` | 自定义模式 UI |
| `_test_connection(role)` | 测试连接按钮逻辑 |
| `_reload_services()` | 保存后热加载全局服务实例 |

---

## 📖 使用示例

### 示例 1: 配置 DeepSeek API

1. 点击侧边栏「⚙️ 设置」
2. 主 LLM 配置 → 标准模式
3. 提供商选择「DeepSeek」
4. 填入 API Key: `sk-xxxxxxxx`
5. 模型选择 `deepseek-chat`
6. 点击「测试连接」→ 显示 ✅ 连接成功
7. 点击「保存配置」

### 示例 2: 配置公司内部 Gemini API

1. 点击侧边栏「⚙️ 设置」
2. 主 LLM 配置 → 自定义模式
3. API URL: `https://internal.company.com/v1beta/models/gemini-2.0-flash:generateContent`
4. API Token: `Bearer your-internal-token`
5. API 格式: Gemini
6. 勾选「自定义 SSL 配置」
7. 测试并保存

### 示例 3: 分离评分 LLM

1. 主 LLM 使用 DeepSeek（如上配置）
2. 评分 LLM 配置区域 → 勾选「启用独立评分 LLM」
3. 选择另一个提供商（如通义千问）
4. 配置并保存

---

## 🔧 配置说明

### 环境变量（.env 方式）

```bash
# 主 LLM（自动检测格式）
LLM_API_URL=https://api.deepseek.com/v1/chat/completions
LLM_BEARER_TOKEN=sk-your-api-key

# 评分 LLM（可选）
DOUBAO_API_KEY=your-key
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=your-model-endpoint
```

### JSON 文件方式

设置页面保存后生成 `data/api_config.json`：

```json
{
  "main_llm": {
    "mode": "standard",
    "provider": "deepseek",
    "api_key": "sk-xxx",
    "model": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 8192
  },
  "scoring_llm": {
    "enabled": false
  }
}
```

### 预设提供商

| 提供商 | 标识 | Base URL | 注册地址 |
|--------|------|----------|---------|
| DeepSeek | `deepseek` | `https://api.deepseek.com/v1` | [platform.deepseek.com](https://platform.deepseek.com) |
| 通义千问 | `qwen` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com) |
| OpenAI | `openai` | `https://api.openai.com/v1` | [platform.openai.com](https://platform.openai.com) |
| Moonshot | `moonshot` | `https://api.moonshot.cn/v1` | [platform.moonshot.cn](https://platform.moonshot.cn) |
| 智谱 GLM | `zhipu` | `https://open.bigmodel.cn/api/paas/v4` | [open.bigmodel.cn](https://open.bigmodel.cn) |
| SiliconFlow | `siliconflow` | `https://api.siliconflow.cn/v1` | [cloud.siliconflow.cn](https://cloud.siliconflow.cn) |

---

## ⚠️ 注意事项

1. **安全性**: `data/api_config.json` 包含 API Key，切勿提交到版本控制（已在 `.gitignore` 保护范围内）
2. **自定义 SSL**: 启用后会降低安全级别并跳过证书验证，仅建议在信任的内部网络使用
3. **向后兼容**: 删除 `data/api_config.json` 即可恢复使用 `.env` 文件配置
4. **评分 LLM 回退**: 未独立配置评分 LLM 时，系统自动使用主 LLM 的配置
5. **热加载限制**: `reload()` 会更新全局服务实例，但已经在进行中的 API 调用不受影响
