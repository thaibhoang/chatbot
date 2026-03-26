from fastapi import APIRouter, UploadFile

from app.models.ingest import IngestResponse
from app.services.rag.pipeline import RAGPipeline

router = APIRouter()


@router.post("", response_model=IngestResponse)
async def ingest_file(project_id: str, file: UploadFile) -> IngestResponse:
    pipeline = RAGPipeline()
    chunks = await pipeline.parse_and_chunk(file=file)
    return IngestResponse(project_id=project_id, chunks=len(chunks), status="processing")
