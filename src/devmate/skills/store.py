import json
import logging
import re
from pathlib import Path

from devmate.config.settings import load_settings
from devmate.skills.schema import Skill

logger = logging.getLogger(__name__)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "skill"


def save_skill(skill: Skill) -> None:
    settings = load_settings()
    skills_dir = Path(settings.skills.skills_dir)
    skills_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{slugify(skill.name)}.json"
    file_path = skills_dir / file_name

    file_path.write_text(
        skill.model_dump_json(indent=2),
        encoding="utf-8",
    )

    logger.info("Skill saved: %s", file_path)