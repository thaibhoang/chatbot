from fastapi import APIRouter

from app.models.query import QueryRequest, QueryResponse
from app.services.rag.pipeline import RAGPipeline

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def run_query(payload: QueryRequest) -> QueryResponse:
    pipeline = RAGPipeline()
    answer = await pipeline.answer_query(
        project_id=payload.project_id,
        query=payload.query,
        use_pro=payload.use_pro,
    )
    return QueryResponse(project_id=payload.project_id, answer=answer)
