import io

from fastapi import UploadFile
from pypdf import PdfReader
from docx import Document

from app.core.settings import get_settings
from app.integrations.gemini_client import GeminiClient
from app.integrations.openai_client import OpenAIClient
from app.integrations.qdrant_client import QdrantStore


class RAGPipeline:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.vector_store = QdrantStore()
        self.openai = OpenAIClient()
        self.gemini = GeminiClient()

    async def parse_and_chunk(self, file: UploadFile) -> tuple[str, list[str]]:
        file_name = file.filename or "document.txt"
        content = await file.read()
        text = self._extract_text(file_name=file_name, content=content)
        chunks = [part.strip() for part in text.split("\n\n") if part.strip()]
        if not chunks and text.strip():
            chunks = [text.strip()]
        return file_name, chunks

    async def ingest_document(self, project_id: str, document_id: str, file: UploadFile) -> int:
        file_name, chunks = await self.parse_and_chunk(file=file)
        embeddings = await self.openai.embed_texts(chunks)
        return await self.vector_store.upsert_document(
            project_id=project_id,
            document_id=document_id,
            file_name=file_name,
            chunks=chunks,
            embeddings=embeddings,
        )

    async def answer_query(self, project_id: str, query: str, use_pro: bool) -> str:
        # Tenant isolation must always be enforced by project_id filter.
        query_embedding = await self.openai.embed_texts([query])
        contexts = await self.vector_store.search(project_id=project_id, query_vector=query_embedding[0])
        if self.settings.llm_provider == "gemini":
            return await self.gemini.generate(query=query, contexts=contexts, use_pro=use_pro)
        return await self.openai.generate(query=query, contexts=contexts, use_pro=use_pro)

    def _extract_text(self, file_name: str, content: bytes) -> str:
        lowered = file_name.lower()
        if lowered.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(content))
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        if lowered.endswith(".docx"):
            doc = Document(io.BytesIO(content))
            return "\n".join([p.text for p in doc.paragraphs])
        return content.decode(errors="ignore")
        return chunks

    async def answer_query(self, project_id: str, query: str, use_pro: bool) -> str:
        # Tenant isolation must always be enforced by project_id filter.
        contexts = await self.vector_store.search(project_id=project_id, query=query)
        return await self.llm.generate(query=query, contexts=contexts, use_pro=use_pro)
