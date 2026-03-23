from pathlib import Path

from langchain_core.documents import Document


def load_markdown_documents(docs_dir: Path) -> list[Document]:
    documents: list[Document] = []

    for file_path in docs_dir.glob("*.md"):
        content = file_path.read_text(encoding="utf-8")
        documents.append(
            Document(
                page_content=content,
                metadata={"source": str(file_path.name)},
            )
        )

    return documents