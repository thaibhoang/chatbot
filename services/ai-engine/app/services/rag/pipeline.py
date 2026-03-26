from fastapi import UploadFile

from app.integrations.gemini_client import GeminiClient
from app.integrations.qdrant_client import QdrantStore


class RAGPipeline:
    def __init__(self) -> None:
        self.vector_store = QdrantStore()
        self.llm = GeminiClient()

    async def parse_and_chunk(self, file: UploadFile) -> list[str]:
        content = (await file.read()).decode(errors="ignore")
        chunks = [part.strip() for part in content.split("\n\n") if part.strip()]
        return chunks

    async def answer_query(self, project_id: str, query: str, use_pro: bool) -> str:
        # Tenant isolation must always be enforced by project_id filter.
        contexts = await self.vector_store.search(project_id=project_id, query=query)
        return await self.llm.generate(query=query, contexts=contexts, use_pro=use_pro)
