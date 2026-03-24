from pathlib import Path

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from devmate.config import load_settings


# ⭐⭐⭐ 新增：模块级缓存
_VECTOR_STORE = None


def get_embeddings():
    settings = load_settings()

    # Ollama embeddings endpoint 不需要 /v1
    base_url = settings.model.ai_base_url.replace("/v1", "")

    return OllamaEmbeddings(
        model=settings.model.embedding_model_name,
        base_url=base_url,
    )


def get_vector_store():
    """
    ⭐ 向量库单例模式
    第一次创建
    后续全部复用
    """
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