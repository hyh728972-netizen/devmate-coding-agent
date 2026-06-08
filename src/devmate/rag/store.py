from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from devmate.config import load_settings


_VECTOR_STORE = None


def get_embeddings():
    settings = load_settings()

    return OpenAIEmbeddings(
        model=settings.model.embedding_model_name,
        base_url=settings.model.ai_base_url,
        api_key=settings.model.api_key,
    )


def get_vector_store():
    global _VECTOR_STORE

    if _VECTOR_STORE is not None:
        return _VECTOR_STORE

    settings = load_settings()

    root = Path(__file__).resolve().parents[3]
    persist_directory = root / settings.rag.persist_dir

    _VECTOR_STORE = Chroma(
        collection_name="devmate_docs",
        embedding_function=get_embeddings(),
        persist_directory=str(persist_directory),
    )

    return _VECTOR_STORE
