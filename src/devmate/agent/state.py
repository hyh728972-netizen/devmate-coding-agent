from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class AgentState:
    goal: str

    # ⭐⭐⭐ 新增
    task_type: str = "DEV_TASK"

    step_count: int = 0
    max_steps: int = 6

    history: List[Dict[str, Any]] = field(default_factory=list)

    rag_context: str = ""
    web_context: str = ""

    generated_files: List[str] = field(default_factory=list)

    finished: bool = False