# DevMate 问题修复清单

## 问题 1：`search_rag` 未注册为 LangChain Tool（严重）✅ 已修复

- **文件**: `src/devmate/agent/tools.py`
- **现象**: `search_rag` 是普通 Python 函数，缺少 `@tool` 装饰器
- **影响**: `create_deep_agent` 无法识别并调用该工具，RAG 检索功能失效
- **修复**: 添加 `@tool` 装饰器，补充完整 docstring 供 LLM 理解工具用途

## 问题 2：`router.py`、`planner.py`、`state.py` 是死代码 ✅ 已修复

- **文件**: `src/devmate/agent/router.py`, `planner.py`, `state.py`
- **现象**: 三个模块没有任何地方 import 使用
- **影响**: Intent Router 和 Planner 逻辑从未执行，代码冗余
- **修复**: 将 router 接入 `runtime.py` 的 `run_agent()` 主流程，意图识别结果记录到日志和 LangSmith Trace

## 问题 3：Skill 复用机制未接入主流程 ✅ 已修复

- **文件**: `src/devmate/agent/runtime.py`
- **现象**: `find_similar_skill()` 已实现但从未被调用
- **影响**: Agent 每次运行都不复用已有 Skill，丢失技能复用能力
- **修复**: 新增 `_build_user_message()` 函数，调用 `find_similar_skill` 匹配已有 Skill，将匹配到的 Skill 上下文注入用户消息

## 问题 4：实际可运行性未验证 ⏳ 待验证

- **文件**: 全局
- **现象**: 项目从未实际启动运行
- **影响**: 无法确认 MCP Server、Agent、RAG、Docker 能否正常工作
- **修复**: 需要实际启动 MCP Server 和 Agent 进行端到端测试
- **前置条件**: 需要安装 Ollama + 模型，配置 Tavily API Key，配置 LangSmith API Key
