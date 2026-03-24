from pathlib import Path
from devmate.config.settings import load_settings

settings = load_settings()

# ⭐ workspace root
WORKSPACE_ROOT = Path(settings.workspace.root).resolve()
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)


def resolve_workspace_path(path: str) -> Path:
    """
    ⭐ 安全路径解析（防止路径越界）
    """

    candidate = (WORKSPACE_ROOT / path).resolve()

    # ⭐ Python 3.9+ 推荐安全判断
    try:
        candidate.relative_to(WORKSPACE_ROOT)
    except ValueError:
        raise ValueError(f"Unsafe path outside workspace: {path}")

    return candidate


def write_file(path: str, content: str) -> str:
    file_path = resolve_workspace_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"WRITE_OK: {path}"


def append_file(path: str, content: str) -> str:
    file_path = resolve_workspace_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content)

    return f"APPEND_OK: {path}"


def read_file(path: str) -> str:
    file_path = resolve_workspace_path(path)

    if not file_path.exists():
        return "FILE_NOT_FOUND"

    return file_path.read_text(encoding="utf-8")


def list_tree() -> str:
    files = []
    for p in WORKSPACE_ROOT.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(WORKSPACE_ROOT)))
    return "\n".join(files)