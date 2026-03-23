from pydantic import BaseModel
from typing import List


class Skill(BaseModel):
    name: str
    task_pattern: str
    file_plan: List[str]
    tool_usage: List[str]
    prompt_template: str