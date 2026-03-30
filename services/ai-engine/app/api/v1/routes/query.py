import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

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


@router.post(":stream")
async def run_query_stream(payload: QueryRequest) -> StreamingResponse:
    pipeline = RAGPipeline()

    async def event_generator():
        try:
            async for token in pipeline.answer_query_stream(
                project_id=payload.project_id,
                query=payload.query,
                use_pro=payload.use_pro,
            ):
                yield f"event: token\ndata: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
            yield "event: done\ndata: {}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'error': str(exc)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
