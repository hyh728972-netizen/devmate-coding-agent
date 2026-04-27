import json
import logging
import re
from hashlib import sha1
from pathlib import Path

from devmate.config.settings import load_settings
from devmate.skills.schema import Skill

logger = logging.getLogger(__name__)


def slugify(text: str) -> str:
    text = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", text)
    slug = re.sub(r"-+", "-", slug).strip("-")
    digest = sha1(text.encode("utf-8")).hexdigest()[:8]
    if not slug:
        slug = "skill"
    return f"{slug[:40].strip('-')}-{digest}"


def _yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _render_skill_markdown(skill: Skill) -> str:
    tool_usage = ", ".join(skill.tool_usage) or "Deep Agents planning tools"
    file_plan = "\n".join(
        f"{index}. Create or update `{path}` when the task requires it."
        for index, path in enumerate(skill.file_plan, start=1)
    )
    if not file_plan:
        file_plan = "1. Inspect the workspace before creating or editing files."

    return (
        "---\n"
        f"name: {_yaml_string(skill.name)}\n"
        f"description: {_yaml_string(skill.task_pattern)}\n"
        "metadata:\n"
        "  owner: devmate\n"
        "  source: generated\n"
        "---\n\n"
        f"# {skill.name}\n\n"
        "## Overview\n\n"
        f"Use this skill for tasks similar to: {skill.task_pattern}\n\n"
        "## Instructions\n\n"
        "1. Start with Deep Agents planning and todo tools.\n"
        "2. Retrieve local context with `search_rag` when project rules or "
        "documents may affect the answer.\n"
        "3. Use the MCP-backed `search_web` tool for current external "
        "framework, package, or API information.\n"
        f"4. Preferred tool pattern: {tool_usage}.\n"
        "5. Keep all generated or modified code inside the configured "
        "workspace unless the user explicitly requests otherwise.\n\n"
        "## File Plan\n\n"
        f"{file_plan}\n\n"
        "## Prompt Template\n\n"
        f"{skill.prompt_template}\n"
    )


def save_skill(skill: Skill) -> None:
    settings = load_settings()
    skills_dir = Path(settings.skills.skills_dir)
    skills_dir.mkdir(parents=True, exist_ok=True)

    skill_dir = skills_dir / slugify(skill.name)
    skill_dir.mkdir(parents=True, exist_ok=True)
    file_path = skill_dir / "SKILL.md"

    file_path.write_text(
        _render_skill_markdown(skill),
        encoding="utf-8",
    )

    logger.info("Skill saved: %s", file_path)