import logging

from langsmith import traceable

from devmate.agent.state import AgentState
from devmate.agent.planner import plan_task
from devmate.agent.tools import (
    list_tree,
    read_file,
    search_rag,
    search_web,
)
from devmate.config.settings import load_settings

from devmate.skills.builder import build_skill_from_run
from devmate.skills.retriever import find_similar_skill
from devmate.skills.store import save_skill

logger = logging.getLogger(__name__)


@traceable(name="skill_recall")
def traced_find_similar_skill(goal: str):
    return find_similar_skill(goal)


@traceable(name="search_rag_tool")
def traced_search_rag(query: str) -> str:
    return search_rag(query)


@traceable(name="search_web_tool")
def traced_search_web(query: str) -> str:
    return search_web(query)


@traceable(name="list_tree_tool")
def traced_list_tree() -> str:
    return list_tree()


@traceable(name="read_file_tool")
def traced_read_file(path: str) -> str:
    return read_file(path)


@traceable(name="skill_save")
def traced_save_skill(goal: str, current_plan: dict, observations: list[str]) -> None:
    skill = build_skill_from_run(
        goal=goal,
        current_plan=current_plan,
        observations=observations,
    )
    save_skill(skill)


@traceable(name="agent_run")
def run_agent(goal: str):
    settings = load_settings()
    state = AgentState(goal=goal)

    skill = traced_find_similar_skill(goal)
    if skill:
        logger.info("Reusing skill: %s", skill.name)
        return {
            "action": "PLAN_CODE",
            "files_to_create": skill.file_plan,
            "steps": ["Reused from skill memory"],
        }

    max_steps = 8

    while not state.finished:
        if state.step_count >= max_steps:
            logger.warning("Agent reached MAX_STEPS → force finish")
            break

        logger.info("Agent step %s", state.step_count)

        decision = plan_task(
            goal=state.goal,
            rag_context=state.rag_context,
            web_context=state.web_context,
            observations=state.observations,
            model=settings.model.model_name,
            base_url=settings.model.ai_base_url,
            api_key=settings.model.api_key,
        )

        action = decision.get("action", "PLAN_CODE")
        logger.info("Agent decision: %s", action)

        if action == "SEARCH_RAG":
            result = traced_search_rag(state.goal)
            state.rag_context = result
            state.observations.append("rag searched")
            state.step_count += 1
            continue

        if action == "SEARCH_WEB":
            result = traced_search_web(state.goal)
            state.web_context = result
            state.observations.append("web searched")
            state.step_count += 1
            continue

        if action == "LIST_TREE":
            tree = traced_list_tree()
            state.observations.append(f"project files:\n{tree[:500]}")
            state.step_count += 1
            continue

        if action == "READ_FILE":
            content = traced_read_file("main.py")
            state.observations.append(
                f"file content preview:\n{content[:500]}"
            )
            state.step_count += 1
            continue

        if action == "PLAN_CODE":
            if state.current_plan is not None:
                logger.info("Plan already exists → agent decides to finish")
                state.finished = True
                break

            state.current_plan = decision
            state.observations.append("plan generated")
            state.step_count += 1
            continue

        if action == "FINISH":
            state.finished = True
            break

        logger.warning("Unknown action → force finish")
        break

    if state.current_plan is not None:
        try:
            traced_save_skill(
                goal=state.goal,
                current_plan=state.current_plan,
                observations=state.observations,
            )
        except Exception:
            logger.exception("Skill save failed")

    return state.current_plan