from pydantic import BaseModel


class KnowledgeResult(BaseModel):
    content: str
    source: str