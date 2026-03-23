from devmate.skills.schema import Skill


def build_skill_from_run(
    goal: str,
    current_plan: dict | None,
    observations: list[str],
) -> Skill:
    files = []
    if current_plan:
        files = current_plan.get("files_to_create", [])

    tool_usage = []
    for item in observations:
        if "rag" in item.lower():
            tool_usage.append("SEARCH_RAG")
        elif "web" in item.lower():
            tool_usage.append("SEARCH_WEB")
        elif "project files" in item.lower():
            tool_usage.append("LIST_TREE")
        elif "file content preview" in item.lower():
            tool_usage.append("READ_FILE")

    # 去重但保持顺序
    deduped_tool_usage = list(dict.fromkeys(tool_usage))

    prompt_template = (
        f"Goal: {goal}\n"
        f"Use similar workflow for tasks like this.\n"
    )

    return Skill(
        name=goal,
        task_pattern=goal,
        file_plan=files,
        tool_usage=deduped_tool_usage,
        prompt_template=prompt_template,
    )