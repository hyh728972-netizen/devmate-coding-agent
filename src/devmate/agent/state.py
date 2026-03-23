from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class AgentState:
    goal: str

    rag_context: str = ""
    web_context: str = ""

    observations: List[str] = field(default_factory=list)

    current_plan: Dict[str, Any] | None = None

    finished: bool = False
    step_count: int = 0