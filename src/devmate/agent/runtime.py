import logging

from langchain_ollama import ChatOllama

from devmate.agent.state import AgentState
from devmate.agent.router import route_intent
from devmate.agent.planner import plan_next_step, generate_code_plan
from devmate.agent.tools import (
    list_tree,
    write_file_tool,
    search_rag,
    search_web,
)
from devmate.config.settings import load_settings

logger = logging.getLogger(__name__)


FILE_GEN_SYSTEM_PROMPT = """
你是专业的软件工程师。

你的任务是：
根据用户需求和文件职责，生成某一个文件的完整可运行内容。

要求：
1. 只输出文件内容本身
2. 不要输出 markdown 代码块
3. 内容要尽量完整、可运行
4. 保持工程化风格，避免无意义注释
5. 如果是 HTML/CSS/JS，要生成合理页面
6. 如果是 Python/FastAPI，要生成最小可运行版本
"""


def _build_file_generation_prompt(
    goal: str,
    file_path: str,
    file_description: str,
    plan_summary: str,
    workspace_tree: str,
    rag_context: str,
    web_context: str,
) -> str:
    return f"""
用户总目标：
{goal}

当前计划摘要：
{plan_summary}

当前要生成的文件：
{file_path}

该文件职责：
{file_description}

当前工作区结构：
{workspace_tree or "空"}

本地知识：
{rag_context or "无"}

互联网知识：
{web_context or "无"}

请直接生成这个文件的完整内容。
"""


def _generate_file_content(
    goal: str,
    file_path: str,
    file_description: str,
    plan_summary: str,
    workspace_tree: str,
    rag_context: str,
    web_context: str,
    model: str,
    base_url: str,
    api_key: str,
) -> str:
    llm = ChatOllama(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=0.2,
    )

    prompt = _build_file_generation_prompt(
        goal=goal,
        file_path=file_path,
        file_description=file_description,
        plan_summary=plan_summary,
        workspace_tree=workspace_tree,
        rag_context=rag_context,
        web_context=web_context,
    )

    resp = llm.invoke([
        {"role": "system", "content": FILE_GEN_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    content = resp.content if isinstance(resp.content, str) else str(resp.content)
    return content.strip()


def _execute_code_plan(
    state: AgentState,
    model: str,
    base_url: str,
    api_key: str,
) -> list[str]:
    created_files: list[str] = []

    if not state.current_plan:
        logger.warning("No current_plan found")
        return created_files

    files = state.current_plan.get("files_to_create", [])
    plan_summary = state.current_plan.get("summary", state.goal)

    for item in files:
        file_path = item.get("file")
        file_description = item.get("description", "")

        if not file_path:
            continue

        logger.info("Generating file content via LLM: %s", file_path)

        workspace_tree = list_tree()
        content = _generate_file_content(
            goal=state.goal,
            file_path=file_path,
            file_description=file_description,
            plan_summary=plan_summary,
            workspace_tree=workspace_tree,
            rag_context=state.rag_context,
            web_context=state.web_context,
            model=model,
            base_url=base_url,
            api_key=api_key,
        )

        result = write_file_tool(file_path, content)
        logger.info("Write file result | path=%s | result=%s", file_path, result)

        if result == "WRITE_OK":
            created_files.append(file_path)
            state.observations.append(f"file created: {file_path}")
        else:
            state.observations.append(f"file create failed: {file_path} | {result}")

    return created_files


def run_agent(goal: str) -> dict:
    logger.info("智能体运行已启动")

    settings = load_settings()
    state = AgentState(goal=goal)

    intent = route_intent(goal)
    logger.info("Intent router decision: %s", intent)

    for step in range(settings.agent.max_steps):
        logger.info("Agent step %s", step)

        decision = plan_next_step(
            goal=state.goal,
            rag_context=state.rag_context,
            web_context=state.web_context,
            observations=state.observations,
            model=settings.model.model_name,
            base_url=settings.model.ai_base_url,
            api_key=settings.model.api_key,
        )

        action = decision.get("action", "FINISH")
        logger.info("Agent decision: %s", action)

        if action == "LIST_TREE":
            tree = list_tree()
            state.observations.append(f"workspace tree:\n{tree}")
            continue

        if action == "SEARCH_RAG":
            state.rag_context = search_rag(state.goal)
            state.observations.append("rag search completed")
            continue

        if action == "SEARCH_WEB":
            state.web_context = search_web(state.goal)
            state.observations.append("web search completed")
            continue

        if action == "PLAN_CODE":
            logger.info("Entering PLAN_CODE phase")

            workspace_tree = list_tree()
            state.current_plan = generate_code_plan(
                goal=state.goal,
                rag_context=state.rag_context,
                web_context=state.web_context,
                workspace_tree=workspace_tree,
                model=settings.model.model_name,
                base_url=settings.model.ai_base_url,
                api_key=settings.model.api_key,
            )

            state.observations.append(
                f"code plan generated: {len(state.current_plan.get('files_to_create', []))} files"
            )

            created_files = _execute_code_plan(
                state=state,
                model=settings.model.model_name,
                base_url=settings.model.ai_base_url,
                api_key=settings.model.api_key,
            )

            return {
                "answer": "DevMate 已完成代码生成",
                "created_files": created_files,
                "plan": state.current_plan,
            }

        if action == "FINISH":
            logger.info("Agent finish decision reached")
            return {
                "answer": "DevMate 已完成任务",
                "created_files": [],
                "plan": state.current_plan,
            }

        logger.warning("Unknown action → force finish")
        return {
            "answer": f"未知动作: {action}",
            "created_files": [],
            "plan": state.current_plan,
        }

    logger.warning("Agent reached MAX_STEPS")
    return {
        "answer": "Agent 达到最大步骤，任务结束",
        "created_files": [],
        "plan": state.current_plan,
    }