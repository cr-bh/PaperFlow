# 更新日志 v1.5.0

## 📅 更新日期
2026-02-28

## 🎯 更新概述
新增图形化 API 设置页面，支持标准提供商预设（DeepSeek/通义千问/OpenAI 等）和自定义 API 两种接入方式。重构 LLM 服务层以统一支持 OpenAI 兼容格式和 Gemini 格式，同时向后兼容现有 `.env` 配置。

## ✨ 新增功能

### 1. API 设置页面 (`ui/settings.py`)
- 全新侧边栏「⚙️ 设置」入口
- **标准模式**: 下拉选择主流 API 提供商，自动填充 Base URL 和模型列表
  - 支持 DeepSeek、通义千问、OpenAI、Moonshot、智谱 GLM、SiliconFlow 六大提供商
- **自定义模式**: 手动填写 API URL / Token / 格式 / SSL 配置
  - 适配公司内部部署的 Gemini 格式 API
- **双 LLM 角色配置**:
  - 主 LLM: 论文总结、思维导图、标签生成、RAG 问答
  - 评分 LLM: Auto-Scholar 评分与 PDF 元数据提取（默认复用主 LLM，可独立配置）
- 参数调节: Temperature 和 Max Tokens 滑块/输入框
- 一键「测试连接」验证 API 可用性
- 配置状态总览显示当前生效的 API 信息

### 2. API 配置管理器 (`services/api_config.py`)
- 预设六大提供商信息（Base URL、模型列表、官方文档链接）
- 配置持久化至 `data/api_config.json`
- 三级配置回退: JSON 文件 → `.env` 环境变量 → 默认空配置
- API 格式自动检测：从 URL 关键词判断 OpenAI 或 Gemini 格式
- `.env` 回退时自动设置自定义 SSL 标记

### 3. 统一 LLM 服务层 (`services/llm_service.py`)
- 重构为同时支持 OpenAI 兼容和 Gemini 两种 API 格式
- 基于 `role` 参数动态加载配置（`main_llm` / `scoring_llm`）
- 运行时热加载: `reload()` 方法在设置页面保存后立即生效
- 延迟验证: 未配置状态下可正常导入，首次调用时检查并给出友好提示
- 新增 `test_connection()` 方法用于设置页面连接测试

## 🏗️ 技术架构

### 新增文件
- `services/api_config.py` - API 配置管理器（预设提供商、JSON 持久化、格式检测）
- `ui/settings.py` - 设置页面 UI 组件

### 修改文件
- `services/llm_service.py` - 重构为统一多格式 LLM 服务
- `services/doubao_service.py` - 简化为 `LLMService` 子类，角色为 `scoring_llm`
- `app.py` - 侧边栏新增设置入口和路由

## 📝 使用说明

### 外部用户（开源用户）

1. 启动应用后，点击侧边栏「⚙️ 设置」
2. 在「主 LLM 配置」中选择「标准模式」
3. 选择 API 提供商（如 DeepSeek）
4. 填入 API Key
5. 选择模型
6. 点击「测试连接」确认可用
7. 点击「保存配置」

### 内部用户（使用现有 .env 配置）

无需任何操作。系统自动从 `.env` 读取配置：
- `LLM_API_URL` → 主 LLM 的 API 地址
- `LLM_BEARER_TOKEN` → 主 LLM 的认证令牌
- `DOUBAO_API_KEY` / `DOUBAO_BASE_URL` → 评分 LLM

如需切换提供商，可在设置页面保存新配置（保存后 JSON 文件优先级高于 `.env`）。

## ⚠️ 注意事项

1. **API Key 安全**: 配置文件 `data/api_config.json` 存放在 `data/` 目录下，已被 `.gitignore` 保护
2. **自定义 SSL**: 仅建议在公司内部网络使用，会降低 SSL 安全级别
3. **评分 LLM 独立配置**: 默认关闭（复用主 LLM），开启后可使用不同提供商
4. **向后兼容**: 删除 `data/api_config.json` 即可恢复使用 `.env` 配置
