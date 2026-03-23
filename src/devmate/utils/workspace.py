from pathlib import Path

WORKSPACE = Path.cwd()


def read_file(path: str) -> str:
    file_path = WORKSPACE / path

    if not file_path.exists():
        return "FILE_NOT_FOUND"

    return file_path.read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    file_path = WORKSPACE / path
    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(content, encoding="utf-8")

    return "WRITE_OK"


def append_file(path: str, content: str) -> str:
    file_path = WORKSPACE / path
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content)

    return "APPEND_OK"


def list_tree() -> str:
    tree = []

    for p in WORKSPACE.rglob("*"):
        if p.is_file():
            tree.append(str(p.relative_to(WORKSPACE)))

    return "\n".join(tree)