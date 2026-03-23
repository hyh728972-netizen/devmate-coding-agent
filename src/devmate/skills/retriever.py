import json
from pathlib import Path
from typing import Optional

from devmate.config.settings import load_settings
from devmate.skills.schema import Skill


def load_all_skills() -> list[Skill]:
    settings = load_settings()
    skills_dir = Path(settings.skills.skills_dir)

    skills = []
    if not skills_dir.exists():
        return skills

    for file in skills_dir.glob("*.json"):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            skills.append(Skill(**data))
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