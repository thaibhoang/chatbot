from pydantic import BaseModel


class IngestResponse(BaseModel):
    project_id: str
    chunks: int
    status: str
