from pydantic import BaseModel
from pydantic import field_validator


class QueryRequest(BaseModel):
    project_id: str
    query: str
    use_pro: bool = False
    provider: str | None = None
    model: str | None = None
    api_key: str | None = None

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().lower()
        if normalized not in {"openai", "gemini", "claude"}:
            raise ValueError("provider must be one of: openai, gemini, claude")
        return normalized


class QueryResponse(BaseModel):
    project_id: str
    answer: str
