from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="AI_ENGINE_", extra="ignore")

    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "rag_embeddings"
    gemini_flash_model: str = "gemini-1.5-flash"
    gemini_pro_model: str = "gemini-1.5-pro"
    gemini_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
