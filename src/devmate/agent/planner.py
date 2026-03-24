import json
import logging

from langchain_ollama import ChatOllama
from langsmith import traceable

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
你是 DevMate Coding Agent 的决策大脑。

你的任务是：
根据用户目标、已有上下文、历史观察，决定下一步最合理的行动。

你只能输出以下 action 之一：
- LIST_TREE
- SEARCH_RAG
- SEARCH_WEB
- PLAN_CODE
- FINISH

规则：
1. 如果用户目标是开发网站、系统、页面、API、应用、脚本、项目结构，优先输出 PLAN_CODE
2. 如果用户问题是本地知识问答，输出 SEARCH_RAG
3. 如果用户问题需要最新互联网信息，输出 SEARCH_WEB
4. 如果信息已经足够，或者任务已经完成，输出 FINISH
5. 不要输出多余解释，只输出 JSON
"""


PLAN_SYSTEM_PROMPT = """
你是 DevMate 的代码规划器。

你的任务：
根据用户需求，生成一个结构化开发计划。

必须输出 JSON，格式如下：
{
  "summary": "一句话总结要做什么",
  "files_to_create": [
    {
      "file": "相对路径",
      "description": "这个文件负责什么"
    }
  ]
}

要求：
1. 文件路径必须是相对路径
2. 文件数量尽量精简，但要保证可运行
3. 如果是前端页面，至少包含 html/css/js 或 React 关键文件
4. 如果是 FastAPI 项目，至少包含 app/main.py 或 main.py
5. 不要输出 markdown 代码块，只输出 JSON
"""


def _build_llm(model: str, base_url: str, api_key: str, temperature: float = 0.1):
    return ChatOllama(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature,
    )


def _safe_parse_json(text: str, fallback: dict) -> dict:
    try:
        return json.loads(text)
    except Exception:
        logger.warning("JSON parse failed, raw text: %s", text)
        return fallback


@traceable(name="planner_step")
def plan_next_step(
    goal: str,
    rag_context: str,
    web_context: str,
    observations: list[str],
    model: str,
    base_url: str,
    api_key: str,
) -> dict:
    llm = _build_llm(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=0.1,
    )

    user_prompt = f"""
GOAL:
{goal}

RAG_CONTEXT:
{rag_context or "无"}

WEB_CONTEXT:
{web_context or "无"}

OBSERVATIONS:
{chr(10).join(observations) if observations else "无"}

请输出：
{{"action":"xxx"}}
"""

    resp = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])

    text = resp.content if isinstance(resp.content, str) else str(resp.content)
    decision = _safe_parse_json(text, {"action": "FINISH"})

    action = decision.get("action", "FINISH")
    logger.info("Planner decision parsed: %s", action)
    return {"action": action}


@traceable(name="generate_code_plan")
def generate_code_plan(
    goal: str,
    rag_context: str,
    web_context: str,
    workspace_tree: str,
    model: str,
    base_url: str,
    api_key: str,
) -> dict:
    llm = _build_llm(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=0.2,
    )

    user_prompt = f"""
用户需求：
{goal}

当前工作区结构：
{workspace_tree or "空"}

本地知识：
{rag_context or "无"}

互联网知识：
{web_context or "无"}

请输出结构化开发计划 JSON。
"""

    resp = llm.invoke([
        {"role": "system", "content": PLAN_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])

    text = resp.content if isinstance(resp.content, str) else str(resp.content)
    fallback = {
        "summary": goal,
        "files_to_create": [
            {
                "file": "generated_project/README.md",
                "description": "项目说明文件"
            }
        ],
    }
    plan = _safe_parse_json(text, fallback)

    if "files_to_create" not in plan or not isinstance(plan["files_to_create"], list):
        plan = fallback

    logger.info("Code plan generated with %s files", len(plan["files_to_create"]))
    return plan