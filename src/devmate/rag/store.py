from pathlib import Path

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from devmate.config import load_settings


def get_embeddings():
    settings = load_settings()

    # Ollama 的 embeddings endpoint 不需要 /v1
    base_url = settings.model.ai_base_url.replace("/v1", "")

    return OllamaEmbeddings(
        model=settings.model.embedding_model_name,
        base_url=base_url,
    )


def get_vector_store():
    root = Path(__file__).resolve().parents[3]
    persist_directory = root / "data" / "chroma"

    return Chroma(
        collection_name="devmate_docs",
        embedding_function=get_embeddings(),
        persist_directory=str(persist_directory),
    )