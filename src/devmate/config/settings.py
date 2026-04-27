from pathlib import Path
import os
import tomllib
from pydantic import BaseModel


class ModelSettings(BaseModel):
    model_provider: str = "ollama"
    ai_base_url: str
    api_key: str
    model_name: str
    embedding_model_name: str


class SearchSettings(BaseModel):
    tavily_api_key: str


class LangSmithSettings(BaseModel):
    langchain_tracing_v2: bool
    langchain_api_key: str
    project: str = "devmate-agent"


class SkillsSettings(BaseModel):
    skills_dir: str
    persist_dir: str = "data/skills"


class WorkspaceSettings(BaseModel):
    root: str
    auto_create: bool = True


class MCPSettings(BaseModel):
    server_url: str
    host: str = "0.0.0.0"
    port: int = 8001
    path: str = "/mcp"
    timeout: int = 30


class AgentRuntimeSettings(BaseModel):
    max_steps: int
    planning_temperature: float


class RAGSettings(BaseModel):
    docs_dir: str
    persist_dir: str


class Settings(BaseModel):
    model: ModelSettings
    search: SearchSettings
    langsmith: LangSmithSettings
    skills: SkillsSettings
    workspace: WorkspaceSettings
    mcp: MCPSettings
    agent: AgentRuntimeSettings
    rag: RAGSettings


def _apply_env_overrides(data: dict) -> dict:
    model = data.setdefault("model", {})
    search = data.setdefault("search", {})
    langsmith = data.setdefault("langsmith", {})

    model_provider = os.getenv("DEVMATE_MODEL_PROVIDER")
    model_name = os.getenv("DEVMATE_MODEL_NAME")
    embedding_model = os.getenv("DEVMATE_EMBEDDING_MODEL_NAME")
    ai_base_url = os.getenv("DEVMATE_AI_BASE_URL")
    model_api_key = os.getenv("DEVMATE_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
    langsmith_project = os.getenv("LANGSMITH_PROJECT")
    mcp_server_url = os.getenv("DEVMATE_MCP_SERVER_URL")
    mcp_host = os.getenv("DEVMATE_MCP_HOST")
    mcp_port = os.getenv("DEVMATE_MCP_PORT")

    if model_provider:
        model["model_provider"] = model_provider
    if model_name:
        model["model_name"] = model_name
    if embedding_model:
        model["embedding_model_name"] = embedding_model
    if ai_base_url:
        model["ai_base_url"] = ai_base_url
    if model_api_key:
        model["api_key"] = model_api_key
    if tavily_api_key:
        search["tavily_api_key"] = tavily_api_key
    if langsmith_api_key:
        langsmith["langchain_api_key"] = langsmith_api_key
    if langsmith_project:
        langsmith["project"] = langsmith_project
    mcp = data.setdefault("mcp", {})
    if mcp_server_url:
        mcp["server_url"] = mcp_server_url
    if mcp_host:
        mcp["host"] = mcp_host
    if mcp_port:
        mcp["port"] = int(mcp_port)

    return data


def load_settings() -> Settings:
    """
    从项目根目录读取 config.toml
    """
    root = Path(__file__).resolve().parents[3]
    config_file = root / "config.toml"

    with open(config_file, "rb") as f:
        data = tomllib.load(f)

    data = _apply_env_overrides(data)
    settings = Settings(**data)

    workspace_path = (root / settings.workspace.root).resolve()
    if settings.workspace.auto_create:
        workspace_path.mkdir(parents=True, exist_ok=True)

    return settings
