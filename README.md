# DevMate Coding Agent

DevMate 是一个 **本地运行的 AI Coding Agent 系统**，  
具备任务理解、RAG 检索、联网搜索、自动代码生成等完整能力，  
模拟真实 AI Agent 工业级架构设计。

该项目适用于：

- AI Agent 工程实践
- Coding Agent 面试项目
- LLM 应用系统设计
- 本地 AI 自动开发助手

---

## 核心能力

### Intent Router（任务意图识别）

系统首先对用户输入进行任务分类：

- `DEV_TASK` → 自动生成代码工程
- `QA_LOCAL` → 本地知识库问答
- `QA_WEB` → 联网搜索问答

实现 **Agent 智能任务调度入口层**

---

### RAG 本地知识库

支持完整 RAG Pipeline：

- 文档加载（PDF / Markdown / TXT）
- Chunk 切分
- Embedding 向量化
- Chroma 向量存储
- Top-k 语义检索

适用于：

- 企业知识问答
- 技术文档理解
- 项目架构总结

---

### MCP 联网搜索

通过 MCP Server 实现：

- Tavily Web Search
- Streamable HTTP Tool 调用
- 实时联网信息获取

Agent 可自动判断：

- 是否需要联网
- 是否需要本地知识

---

### Agent 决策循环（ReAct Loop）

Agent Runtime 实现完整推理循环：

- Planner 决策 Action
- Tool 执行
- 状态更新
- 多步推理

支持核心 Action：

SEARCH_RAG
SEARCH_WEB
PLAN_CODE
LIST_TREE
ANSWER


---

# 环境安装

## ① 安装 uv（推荐）
pip install uv


---

## ② 安装 Python 依赖
uv sync


---

# 本地模型安装（必须）

DevMate 使用 **Ollama 本地模型**

先安装 Ollama：

https://ollama.com

然后拉模型：
ollama pull qwen2.5:7b-instruct
ollama pull nomic-embed-text


---

# 启动 MCP 搜索服务

在项目根目录执行：
uv run --directory src uvicorn devmate.mcp.server:app --port 8001


---

# 启动 Coding Agent

新开一个终端：
uv run --directory src python -m devmate.agent.executor

出现：
请输入你的开发任务需求：

说明 Agent 已启动 ✅

---

# 💬 示例 1：本地知识问答

输入：
DevMate系统有什么核心模块

Agent 自动执行流程：
Intent Router → QA_LOCAL
RAG 检索
LLM 总结

示例输出：
DevMate 核心模块包括：

Agent Runtime 推理循环
Intent Router 任务识别
RAG 本地知识库
MCP 联网搜索
Workspace Coding Tools


---

# 💬 示例 2：自动生成代码

输入：
帮我做一个徒步网站