from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "rag_embeddings"
    gemini_flash_model: str = "gemini-1.5-flash"
    gemini_pro_model: str = "gemini-1.5-pro"
    gemini_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
