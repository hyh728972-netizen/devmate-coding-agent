import logging

from mcp.server.fastmcp import FastMCP

from devmate.config import load_settings
from devmate.mcp.tools import TavilySearchTool

logger = logging.getLogger(__name__)
settings = load_settings()

server = FastMCP(
    name="DevMate Search MCP Server",
    host=settings.mcp.host,
    port=settings.mcp.port,
    streamable_http_path=settings.mcp.path,
    stateless_http=True,
    json_response=True,
)
search_tool: TavilySearchTool | None = None


def _get_search_tool() -> TavilySearchTool:
    global search_tool

    if search_tool is not None:
        return search_tool

    search_tool = TavilySearchTool(settings.search.tavily_api_key)
    return search_tool


@server.tool(
    name="search_web",
    description=(
        "Search the live web with Tavily for current framework, package, "
        "API, and product information."
    ),
)
def search_web(query: str) -> list[dict]:
    """Run Tavily search through the MCP Streamable HTTP server."""
    if not query.strip():
        return []

    logger.info("MCP Tavily search called")
    return _get_search_tool().search(query)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    server.run(transport="streamable-http")


if __name__ == "__main__":
    main()
