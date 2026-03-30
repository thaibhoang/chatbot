from fastapi import APIRouter, UploadFile

from app.models.ingest import IngestResponse
from app.services.rag.pipeline import RAGPipeline

router = APIRouter()


@router.post("", response_model=IngestResponse)
async def ingest_file(project_id: str, document_id: str, file: UploadFile) -> IngestResponse:
    pipeline = RAGPipeline()
    vector_count = await pipeline.ingest_document(project_id=project_id, document_id=document_id, file=file)
    return IngestResponse(project_id=project_id, chunks=vector_count, status="ready")
