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
    qdrant_memory_collection: str = "customer_memories"

    redis_url: str = "redis://redis:6379/0"
    stm_window_size: int = 20
    ltm_limit: int = 5

    postgres_dsn: str = "postgres://omnirag:omnirag@postgres:5432/omnirag"
    memory_job_batch_size: int = 20
    memory_job_poll_seconds: int = 20
    memory_periodic_sweep_seconds: int = 21600
    memory_trigger_message_threshold: int = 8
    memory_trigger_token_threshold: int = 1200
    memory_trigger_cooldown_minutes: int = 45

    openai_extractor_model: str = "gpt-4o-mini"
    gemini_flash_model: str = "gemini-1.5-flash"
    gemini_pro_model: str = "gemini-1.5-pro"
    gemini_api_key: str = ""
    claude_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-latest"


@lru_cache
def get_settings() -> Settings:
    return Settings()
