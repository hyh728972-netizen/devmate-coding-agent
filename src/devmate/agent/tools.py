import logging
import requests
from pathlib import Path

from devmate.rag.retriever import search_knowledge_base
from devmate.config.settings import load_settings
from devmate.utils.workspace import (
    write_file,
    append_file,
    read_file as workspace_read_file,
    list_tree as workspace_list_tree,
)

logger = logging.getLogger(__name__)

# ⭐⭐⭐⭐⭐ 加载配置（统一工程入口）
settings = load_settings()

# ⭐⭐⭐⭐⭐ Workspace 根目录（Agent 沙箱）
PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = (PROJECT_ROOT / settings.workspace.root).resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

# ⭐⭐⭐⭐⭐ MCP 地址配置化
MCP_BASE_URL = settings.mcp.server_url.rstrip("/")


# =========================
# ⭐ RAG TOOL
# =========================
def search_rag(query: str) -> str:
    results = search_knowledge_base(query)

    if not results:
        return ""

    context = "\n\n".join([r.content for r in results])
    return context


# =========================
# ⭐ WEB TOOL (MCP)
# =========================
def search_web(query: str) -> str:
    try:
        resp = requests.post(
            f"{MCP_BASE_URL}/mcp/search",
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


# =========================
# ⭐⭐⭐⭐⭐ WORKSPACE TOOLS
# =========================

def _safe_resolve(path: str) -> Path:
    """
    防止路径越界攻击
    """
    target = (WORKSPACE / path).resolve()

    if WORKSPACE not in target.parents and target != WORKSPACE:
        raise ValueError("非法路径访问（越界 workspace）")

    return target


def list_tree() -> str:
    files = []
    for p in WORKSPACE.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(WORKSPACE)))
    return "\n".join(files)


def read_file(path: str) -> str:
    try:
        file_path = _safe_resolve(path)
    except Exception:
        return "INVALID_PATH"

    if not file_path.exists():
        return "FILE_NOT_FOUND"

    return file_path.read_text(encoding="utf-8")


def write_file_tool(path: str, content: str) -> str:
    try:
        file_path = _safe_resolve(path)
    except Exception:
        return "INVALID_PATH"

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return "WRITE_OK"


def append_file_tool(path: str, content: str) -> str:
    try:
        file_path = _safe_resolve(path)
    except Exception:
        return "INVALID_PATH"

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content)

    return "APPEND_OK"