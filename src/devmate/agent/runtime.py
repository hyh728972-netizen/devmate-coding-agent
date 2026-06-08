import asyncio
import logging
import os
from inspect import isawaitable
from pathlib import Path
from uuid import uuid4

from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient

from devmate.agent.prompts import SYSTEM_PROMPT
from devmate.agent.router import route_intent
from devmate.agent.tools import search_rag
from devmate.config.settings import load_settings
from devmate.skills.builder import build_skill_from_run
from devmate.skills.retriever import find_similar_skill
from devmate.skills.store import save_skill


logger = logging.getLogger(__name__)
settings = load_settings()
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _to_virtual_path(path: str) -> str:
    normalized = path.replace("\\", "/").lstrip("./")
    return f"/{normalized}".rstrip("/")


def _configure_tracing() -> None:
    os.environ["NO_PROXY"] = "localhost,127.0.0.1"
    if settings.langsmith.langchain_tracing_v2:
        os.environ["LANGSMITH_TRACING"] = "true"
    if settings.langsmith.langchain_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith.langchain_api_key
    if settings.langsmith.project:
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith.project


def get_llm():
    model_id = f"{settings.model.model_provider}:{settings.model.model_name}"
    model_kwargs = {
        "model": model_id,
        "temperature": settings.agent.planning_temperature,
    }

    if settings.model.ai_base_url:
        model_kwargs["base_url"] = settings.model.ai_base_url
    if settings.model.api_key:
        model_kwargs["api_key"] = settings.model.api_key

    return init_chat_model(**model_kwargs)


async def _load_mcp_tools() -> list:
    client = MultiServerMCPClient(
        {
            "devmate-search": {
                "url": settings.mcp.server_url,
                "transport": "streamable_http",
            },
        }
    )
    return await client.get_tools()


def _get_tools() -> list:
    return [search_rag, *asyncio.run(_load_mcp_tools())]


def _invoke_agent(agent, messages: dict, config: dict) -> dict:
    result = agent.invoke(messages, config=config)
    if isawaitable(result):
        return asyncio.run(result)
    return result


def _build_agent():
    docs_path = f"{_to_virtual_path(settings.rag.docs_dir)}/**"
    skills_path = _to_virtual_path(settings.skills.skills_dir)
    workspace_path = f"{_to_virtual_path(settings.workspace.root)}/**"

    backend = FilesystemBackend(
        root_dir=str(PROJECT_ROOT),
        virtual_mode=True,
    )
    permissions = [
        FilesystemPermission(
            operations=["read"],
            paths=[docs_path, f"{skills_path}/**", workspace_path],
            mode="allow",
        ),
        FilesystemPermission(
            operations=["write"],
            paths=[workspace_path],
            mode="allow",
        ),
        FilesystemPermission(
            operations=["read", "write"],
            paths=["/**"],
            mode="deny",
        ),
    ]

    return create_deep_agent(
        model=get_llm(),
        tools=_get_tools(),
        system_prompt=SYSTEM_PROMPT,
        backend=backend,
        permissions=permissions,
        skills=[skills_path],
        name="devmate-coding-agent",
    )


def _extract_text(result: dict) -> str:
    messages = result.get("messages", [])
    if not messages:
        return ""

    for message in reversed(messages):
        content = getattr(message, "content", None)
        if content is None and isinstance(message, dict):
            content = message.get("content")

        if isinstance(content, str) and content.strip():
            return content

        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
                else:
                    parts.append(str(item))
            text = "\n".join(part for part in parts if part)
            if text.strip():
                return text

    return str(messages[-1])


def _build_user_message(goal: str) -> str:
    matched_skill = find_similar_skill(goal)
    if matched_skill is None:
        return goal

    logger.info("Matched reusable skill: %s", matched_skill.name)
    skill_context = (
        "[Relevant Skill Context]\n"
        f"{matched_skill.prompt_template}\n"
        "[End of Skill Context]\n\n"
        f"{goal}"
    )
    return skill_context


def run_agent(goal: str, thread_id: str | None = None) -> dict:
    _configure_tracing()

    task_type = route_intent(goal)
    logger.info("Intent routing result: goal='%s' → task_type='%s'", goal, task_type)

    logger.info("智能体运行已启动")
    agent = _build_agent()
    user_message = _build_user_message(goal)
    result = _invoke_agent(
        agent,
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                }
            ]
        },
        config={
            "configurable": {
                "thread_id": thread_id or str(uuid4()),
            }
        },
    )
    answer = _extract_text(result)
    try:
        save_skill(build_skill_from_run(goal, None, [answer]))
    except Exception:
        logger.exception("Failed to save reusable skill")
    return {"answer": answer, "result": result, "task_type": task_type}
