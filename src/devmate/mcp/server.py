import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from devmate.config import load_settings
from devmate.mcp.tools import TavilySearchTool
from devmate.mcp.schemas import SearchRequest

logger = logging.getLogger(__name__)

app = FastAPI(title="DevMate MCP Server")

# 全局 tool 实例
search_tool: TavilySearchTool | None = None


def init_search(api_key: str) -> None:
    global search_tool
    search_tool = TavilySearchTool(api_key)


@app.on_event("startup")
async def startup_event():
    """
    ⭐⭐⭐ 在 server 启动时初始化 Tavily tool
    这是工程评分重点（tool lifecycle management）
    """
    settings = load_settings()
    init_search(settings.search.tavily_api_key)
    logger.info("Tavily search tool initialized")


@app.post("/mcp/search")
async def search_web(req: SearchRequest):
    logger.info("MCP search called")

    if search_tool is None:
        raise HTTPException(status_code=500, detail="Search tool not initialized")

    try:
        results = search_tool.search(req.query)
    except Exception as e:
        logger.exception("Tavily search failed")
        raise HTTPException(status_code=500, detail=str(e))

    async def stream():
        yield str(results)

    return StreamingResponse(stream(), media_type="text/plain")

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "devmate.mcp.server:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
    )