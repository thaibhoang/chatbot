import io
from typing import AsyncIterator

from fastapi import UploadFile
from pypdf import PdfReader
from docx import Document

from app.core.settings import get_settings
from app.integrations.claude_client import ClaudeClient
from app.integrations.gemini_client import GeminiClient
from app.integrations.openai_client import OpenAIClient
from app.integrations.qdrant_client import QdrantStore
from app.services.memory.service import get_memory_service


class InvalidProviderError(ValueError):
    pass


class RAGPipeline:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.vector_store = QdrantStore()
        self.openai = OpenAIClient()
        self.gemini = GeminiClient()
        self.claude = ClaudeClient()
        self.memory = get_memory_service()

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

    async def answer_query(
        self,
        project_id: str,
        customer_id: str,
        query: str,
        conversation_id: str | None,
        use_pro: bool,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ) -> str:
        # Tenant isolation must always be enforced by project_id filter.
        query_embedding = await self.openai.embed_texts([query])
        knowledge_contexts = await self.vector_store.search(project_id=project_id, query_vector=query_embedding[0])
        recent_chat = await self.memory.get_recent_chat(project_id=project_id, customer_id=customer_id)
        long_term_facts = await self.memory.get_long_term_facts(project_id=project_id, customer_id=customer_id, query=query)
        contexts = self._build_context_blocks(knowledge_contexts, recent_chat, long_term_facts)
        resolved_provider = self._resolve_provider(provider)
        _ = conversation_id
        if resolved_provider == "gemini":
            answer = await self.gemini.generate(
                query=query, contexts=contexts, use_pro=use_pro, model=model, api_key=api_key
            )
            await self.memory.post_answer(
                project_id=project_id,
                customer_id=customer_id,
                user_query=query,
                assistant_answer=answer,
            )
            return answer
        if resolved_provider == "claude":
            answer = await self.claude.generate(
                query=query, contexts=contexts, use_pro=use_pro, model=model, api_key=api_key
            )
            await self.memory.post_answer(
                project_id=project_id,
                customer_id=customer_id,
                user_query=query,
                assistant_answer=answer,
            )
            return answer
        answer = await self.openai.generate(query=query, contexts=contexts, use_pro=use_pro, model=model, api_key=api_key)
        await self.memory.post_answer(
            project_id=project_id,
            customer_id=customer_id,
            user_query=query,
            assistant_answer=answer,
        )
        return answer

    async def answer_query_stream(
        self,
        project_id: str,
        customer_id: str,
        query: str,
        conversation_id: str | None,
        use_pro: bool,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ) -> AsyncIterator[str]:
        query_embedding = await self.openai.embed_texts([query])
        knowledge_contexts = await self.vector_store.search(project_id=project_id, query_vector=query_embedding[0])
        recent_chat = await self.memory.get_recent_chat(project_id=project_id, customer_id=customer_id)
        long_term_facts = await self.memory.get_long_term_facts(project_id=project_id, customer_id=customer_id, query=query)
        contexts = self._build_context_blocks(knowledge_contexts, recent_chat, long_term_facts)
        resolved_provider = self._resolve_provider(provider)
        _ = conversation_id
        tokens: list[str] = []
        if resolved_provider == "gemini":
            async for token in self.gemini.generate_stream(
                query=query, contexts=contexts, use_pro=use_pro, model=model, api_key=api_key
            ):
                tokens.append(token)
                yield token
            await self.memory.post_answer(
                project_id=project_id,
                customer_id=customer_id,
                user_query=query,
                assistant_answer="".join(tokens),
            )
            return
        if resolved_provider == "claude":
            async for token in self.claude.generate_stream(
                query=query, contexts=contexts, use_pro=use_pro, model=model, api_key=api_key
            ):
                tokens.append(token)
                yield token
            await self.memory.post_answer(
                project_id=project_id,
                customer_id=customer_id,
                user_query=query,
                assistant_answer="".join(tokens),
            )
            return
        async for token in self.openai.generate_stream(
            query=query, contexts=contexts, use_pro=use_pro, model=model, api_key=api_key
        ):
            tokens.append(token)
            yield token
        await self.memory.post_answer(
            project_id=project_id,
            customer_id=customer_id,
            user_query=query,
            assistant_answer="".join(tokens),
        )

    def _resolve_provider(self, provider: str | None) -> str:
        resolved = (provider or self.settings.llm_provider).strip().lower()
        if resolved not in {"openai", "gemini", "claude"}:
            raise InvalidProviderError(f"unsupported provider: {resolved}")
        return resolved

    def _extract_text(self, file_name: str, content: bytes) -> str:
        lowered = file_name.lower()
        if lowered.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(content))
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        if lowered.endswith(".docx"):
            doc = Document(io.BytesIO(content))
            return "\n".join([p.text for p in doc.paragraphs])
        return content.decode(errors="ignore")

    def _build_context_blocks(
        self,
        knowledge_contexts: list[str],
        recent_chat: list[dict[str, str]],
        long_term_facts: list[str],
    ) -> list[str]:
        blocks: list[str] = []
        if long_term_facts:
            facts_text = "\n".join([f"- {fact}" for fact in long_term_facts[: self.settings.ltm_limit]])
            blocks.append(f"[CustomerFacts]\n{facts_text}")
        if recent_chat:
            history_lines = [f"{item['role']}: {item['content']}" for item in recent_chat[-self.settings.stm_window_size :]]
            blocks.append(f"[RecentChat]\n" + "\n".join(history_lines))
        if knowledge_contexts:
            blocks.append("[KnowledgeBase]\n" + "\n\n".join(knowledge_contexts[:8]))
        return blocks
