from pydantic import BaseModel


class QueryRequest(BaseModel):
    project_id: str
    query: str
    use_pro: bool = False


class QueryResponse(BaseModel):
    project_id: str
    answer: str
