from pathlib import Path
import tomllib
from pydantic import BaseModel


class ModelSettings(BaseModel):
    ai_base_url: str
    api_key: str
    model_name: str
    embedding_model_name: str


class SearchSettings(BaseModel):
    tavily_api_key: str


class LangSmithSettings(BaseModel):
    langchain_tracing_v2: bool
    langchain_api_key: str


class SkillsSettings(BaseModel):
    skills_dir: str


class Settings(BaseModel):
    model: ModelSettings
    search: SearchSettings
    langsmith: LangSmithSettings
    skills: SkillsSettings


def load_settings() -> Settings:
    """
    从项目根目录读取 config.toml
    """
    root = Path(__file__).resolve().parents[3]
    config_file = root / "config.toml"

    with open(config_file, "rb") as f:
        data = tomllib.load(f)

    return Settings(**data)