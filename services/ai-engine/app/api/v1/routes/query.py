import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.query import QueryRequest, QueryResponse
from app.services.rag.pipeline import InvalidProviderError, RAGPipeline

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def run_query(payload: QueryRequest) -> QueryResponse:
    pipeline = RAGPipeline()
    try:
        answer = await pipeline.answer_query(
            project_id=payload.project_id,
            query=payload.query,
            use_pro=payload.use_pro,
            provider=payload.provider,
            model=payload.model,
            api_key=payload.api_key,
        )
    except InvalidProviderError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return QueryResponse(project_id=payload.project_id, answer=answer)


@router.post(":stream")
async def run_query_stream(payload: QueryRequest) -> StreamingResponse:
    pipeline = RAGPipeline()
    try:
        # Validate provider before starting stream so invalid config returns HTTP 400.
        pipeline._resolve_provider(payload.provider)
    except InvalidProviderError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    async def event_generator():
        try:
            async for token in pipeline.answer_query_stream(
                project_id=payload.project_id,
                query=payload.query,
                use_pro=payload.use_pro,
                provider=payload.provider,
                model=payload.model,
                api_key=payload.api_key,
            ):
                yield f"event: token\ndata: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
            yield "event: done\ndata: {}\n\n"
        except InvalidProviderError as exc:
            yield f"event: error\ndata: {json.dumps({'error': str(exc)}, ensure_ascii=False)}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'error': str(exc)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
