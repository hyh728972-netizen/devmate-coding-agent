import logging

from devmate.agent.state import AgentState
from devmate.agent.router import route_intent
from devmate.agent.planner import plan_next_step
from devmate.agent.tools import (
    search_rag,
    search_web,
    list_tree,
    write_file_tool,
)

from langchain_community.chat_models import ChatOllama
from devmate.config.settings import load_settings


logger = logging.getLogger(__name__)
settings = load_settings()


def get_llm():
    return ChatOllama(
        model=settings.model.model_name,
        base_url=settings.model.ai_base_url
    )


def run_agent(goal: str):

    logger.info("智能体运行已启动")

    llm = get_llm()

    state = AgentState(goal=goal)

    # ⭐ intent router
    state.task_type = route_intent(goal)

    logger.info("Intent router decision: %s", state.task_type)

    while not state.finished and state.step_count < state.max_steps:

        logger.info("Agent step %s", state.step_count)

        action = plan_next_step(state, llm)

        logger.info("Agent decision: %s", action)

        # ⭐⭐⭐⭐⭐ LOCAL QA
        if action == "SEARCH_RAG":

            state.rag_context = search_rag(state.goal)

            state.history.append({"action": "SEARCH_RAG"})
            state.step_count += 1
            continue

        # ⭐⭐⭐⭐⭐ WEB QA
        if action == "SEARCH_WEB":

            state.web_context = search_web(state.goal)

            state.history.append({"action": "SEARCH_WEB"})
            state.step_count += 1
            continue

        # ⭐⭐⭐⭐⭐ 工程工具
        if action == "LIST_TREE":

            tree = list_tree()

            state.history.append({"action": "LIST_TREE", "tree": tree})
            state.step_count += 1
            continue

        # ⭐⭐⭐⭐⭐ Coding
        if action == "PLAN_CODE":

            logger.info("Entering PLAN_CODE phase")

            fake_files = [
                "./app/main.py",
                "./config/settings.py",
                "./models/user.py",
                "./routes/auth.py",
                "./routes/api.py",
            ]

            for f in fake_files:

                logger.info("Generating file content via LLM: %s", f)

                content = llm.invoke(f"生成 {f} 文件代码").content

                result = write_file_tool(f, content)

                logger.info("Write file result | path=%s | result=%s", f, result)

            state.finished = True
            return {"answer": "代码生成完成"}

        # ⭐⭐⭐⭐⭐ 最终回答
        if action == "ANSWER":

            answer_prompt = f"""
请基于以下信息回答用户问题

问题:
{state.goal}

本地知识:
{state.rag_context}

网络知识:
{state.web_context}
"""

            answer = llm.invoke(answer_prompt).content

            state.finished = True
            return {"answer": answer}

    return {"answer": "Agent 未完成任务"}