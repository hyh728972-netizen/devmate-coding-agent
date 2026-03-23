from devmate.rag.schemas import KnowledgeResult
from devmate.rag.store import get_vector_store


def search_knowledge_base(query: str, k: int = 3) -> list[KnowledgeResult]:
    vector_store = get_vector_store()
    documents = vector_store.similarity_search(query, k=k)

    results: list[KnowledgeResult] = []

    for document in documents:
        results.append(
            KnowledgeResult(
                content=document.page_content,
                source=document.metadata.get("source", "unknown"),
            )
        )

    return results