import logging

from tavily import TavilyClient

logger = logging.getLogger(__name__)


class TavilySearchTool:
    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("Tavily API key is not configured")
        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str) -> list[dict]:
        logger.info("Running Tavily search for query: %s", query)

        result = self.client.search(
            query=query,
            max_results=5,
        )

        return result.get("results", [])