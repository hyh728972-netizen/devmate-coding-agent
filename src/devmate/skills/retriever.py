from pathlib import Path
from typing import Optional

from devmate.config.settings import load_settings
from devmate.skills.schema import Skill


def _frontmatter_value(markdown: str, key: str) -> str:
    prefix = f"{key}:"
    for line in markdown.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip().strip('"')
    return ""


def _skill_from_markdown(file: Path) -> Skill:
    markdown = file.read_text(encoding="utf-8")
    name = _frontmatter_value(markdown, "name") or file.parent.name
    description = _frontmatter_value(markdown, "description") or name
    return Skill(
        name=name,
        task_pattern=description,
        file_plan=[],
        tool_usage=[],
        prompt_template=markdown,
    )


def load_all_skills() -> list[Skill]:
    settings = load_settings()
    skills_dir = Path(settings.skills.skills_dir)

    skills = []
    if not skills_dir.exists():
        return skills

    for file in skills_dir.glob("*/SKILL.md"):
        try:
            skills.append(_skill_from_markdown(file))
        except Exception:
            continue

    return skills


def find_similar_skill(goal: str) -> Optional[Skill]:
    """
    ⭐ 最小 semantic search v0
    先做 keyword match
    后面可以升级 embedding
    """

    goal_lower = goal.lower()

    for skill in load_all_skills():
        if skill.task_pattern.lower() in goal_lower:
            return skill

    return None