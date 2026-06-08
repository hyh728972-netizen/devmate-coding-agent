from langchain_core.tools import tool

from devmate.rag.retriever import search_knowledge_base


@tool
def search_rag(query: str) -> str:
    """Search the local knowledge base for project documentation, architecture
    guidelines, coding standards, and internal rules. Use this tool before
    relying on general knowledge when the task involves project-specific
    conventions or local documentation.
    """
    results = search_knowledge_base(query)

    if not results:
        return ""

    context = "\n\n".join(
        f"[source: {result.source}]\n{result.content}"
        for result in results
    )
    return context
