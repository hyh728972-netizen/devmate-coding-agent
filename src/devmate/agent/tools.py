import requests
import logging
from pathlib import Path

from devmate.rag.retriever import search_knowledge_base

logger = logging.getLogger(__name__)

WORKSPACE = Path.cwd()

# ⭐ RAG
def search_rag(query: str) -> str:
    results = search_knowledge_base(query)

    if not results:
        return ""

    context = "\n\n".join([r.content for r in results])
    return context


# ⭐ MCP Web
def search_web(query: str) -> str:
    try:
        resp = requests.post(
            "http://127.0.0.1:8001/mcp/search",
            json={"query": query},
            timeout=30,
        )

        if resp.status_code != 200:
            logger.warning("MCP search status %s", resp.status_code)
            return ""

        return resp.text

    except Exception:
        logger.exception("MCP search failed")
        return ""


# ⭐⭐⭐⭐⭐ Workspace Tools

def list_tree() -> str:
    files = []
    for p in WORKSPACE.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(WORKSPACE)))
    return "\n".join(files)


def read_file(path: str) -> str:
    file_path = WORKSPACE / path
    if not file_path.exists():
        return "FILE_NOT_FOUND"
    return file_path.read_text(encoding="utf-8")