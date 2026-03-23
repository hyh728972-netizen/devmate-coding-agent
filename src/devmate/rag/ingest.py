import logging
from pathlib import Path

from devmate.rag.loader import load_markdown_documents
from devmate.rag.chunker import split_documents
from devmate.rag.store import get_vector_store

logger = logging.getLogger(__name__)


def ingest_documents() -> None:
    root = Path(__file__).resolve().parents[3]
    docs_dir = root / "docs"

    logger.info("Docs folder: %s", docs_dir)

    documents = load_markdown_documents(docs_dir)
    logger.info("Loaded documents: %s", len(documents))

    chunks = split_documents(documents)
    logger.info("Chunks created: %s", len(chunks))

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    logger.info("✅ Ingested %s chunks into vector store", len(chunks))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingest_documents()