import json
import logging

from langchain_ollama import ChatOllama
from langsmith import traceable

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are DevMate autonomous coding agent planner.

You must decide NEXT BEST ACTION.

Available actions:

SEARCH_RAG
SEARCH_WEB
LIST_TREE
READ_FILE
PLAN_CODE
FINISH

Rules:

- If lack technical knowledge → SEARCH_WEB
- If need internal docs → SEARCH_RAG
- If need inspect project → LIST_TREE or READ_FILE
- If enough info → PLAN_CODE
- If already produced a plan → FINISH
- You may reuse past skills if they match the task.

Return JSON ONLY:

{
  "action": "...",
  "reason": "...",
  "files_to_create": [],
  "steps": []
}
"""


@traceable(name="planner_llm_call")
def call_planner_llm(llm: ChatOllama, messages: list[dict]):
    return llm.invoke(messages)


@traceable(name="planner_decision")
def plan_task(
    goal: str,
    rag_context: str,
    web_context: str,
    observations: list[str],
    model: str,
    base_url: str,
    api_key: str,
) -> dict:
    llm = ChatOllama(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=0.2,
    )

    user_prompt = f"""
GOAL:
{goal}

RAG CONTEXT:
{rag_context}

WEB CONTEXT:
{web_context}

OBSERVATIONS:
{observations}
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    response = call_planner_llm(llm, messages)
    text = response.content

    try:
        decision = json.loads(text)
    except Exception:
        logger.warning("Planner JSON parse failed → fallback PLAN_CODE")
        decision = {
            "action": "PLAN_CODE",
            "reason": "fallback",
            "files_to_create": [],
            "steps": [],
        }

    logger.info("Planner decision parsed: %s", decision.get("action"))
    return decision