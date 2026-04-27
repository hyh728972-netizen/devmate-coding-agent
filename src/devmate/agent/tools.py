from devmate.rag.retriever import search_knowledge_base


def search_rag(query: str) -> str:
    """
    Search the local knowledge base and return a merged text context.
    """
    results = search_knowledge_base(query)

    if not results:
        return ""

    context = "\n\n".join(
        f"[source: {result.source}]\n{result.content}"
        for result in results
    )
    return context
