import logging

logger = logging.getLogger(__name__)


def plan_next_step(state, llm):

    # ⭐⭐⭐⭐⭐ QA_LOCAL 强硬策略（最高优先级）
    if state.task_type == "QA_LOCAL":

        if not state.rag_context:
            logger.info("Planner decision (QA_LOCAL): SEARCH_RAG")
            return "SEARCH_RAG"

        logger.info("Planner decision (QA_LOCAL): ANSWER")
        return "ANSWER"

    # ⭐⭐⭐⭐⭐ QA_WEB 强硬策略
    if state.task_type == "QA_WEB":

        if not state.web_context:
            logger.info("Planner decision (QA_WEB): SEARCH_WEB")
            return "SEARCH_WEB"

        logger.info("Planner decision (QA_WEB): ANSWER")
        return "ANSWER"

    # ⭐⭐⭐⭐⭐ DEV_TASK 才允许 LLM 自主规划
    prompt = f"""
你是 DevMate Coding Agent Planner

用户目标:
{state.goal}

历史:
{state.history}

你必须只返回一个 action：

可选 action:

PLAN_CODE
LIST_TREE
ANSWER
"""

    result = llm.invoke(prompt).content.strip()

    if "PLAN_CODE" in result:
        logger.info("Planner decision parsed: PLAN_CODE")
        return "PLAN_CODE"

    if "LIST_TREE" in result:
        logger.info("Planner decision parsed: LIST_TREE")
        return "LIST_TREE"

    if "ANSWER" in result:
        logger.info("Planner decision parsed: ANSWER")
        return "ANSWER"

    logger.warning("Planner parse fail → fallback LIST_TREE")
    return "LIST_TREE"