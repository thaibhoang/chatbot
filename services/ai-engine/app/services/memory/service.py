import asyncio
from datetime import UTC, datetime

from app.core.settings import get_settings
from app.integrations.memory_jobs import MemoryJobStore
from app.integrations.openai_client import OpenAIClient
from app.integrations.qdrant_client import QdrantStore
from app.integrations.redis_memory import RedisMemoryStore

SIGNAL_KEYWORDS = (
    "thích",
    "không thích",
    "ưu tiên",
    "vấn đề",
    "lỗi",
    "size",
    "màu",
    "địa chỉ",
    "số điện thoại",
)


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()))


class MemoryService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.redis_store = RedisMemoryStore()
        self.jobs = MemoryJobStore()
        self.vector_store = QdrantStore()
        self.openai = OpenAIClient()
        self._worker_task: asyncio.Task | None = None
        self._sweep_task: asyncio.Task | None = None
        self._stopped = asyncio.Event()
        self._enabled = True

    async def startup(self) -> None:
        try:
            await self.jobs.connect()
            await self.redis_store.client.ping()
        except Exception:
            self._enabled = False
            return
        self._stopped.clear()
        self._worker_task = asyncio.create_task(self._run_worker_loop())
        self._sweep_task = asyncio.create_task(self._run_sweep_loop())

    async def shutdown(self) -> None:
        self._stopped.set()
        if not self._enabled:
            return
        if self._worker_task is not None:
            self._worker_task.cancel()
        if self._sweep_task is not None:
            self._sweep_task.cancel()
        await self.jobs.close()
        await self.redis_store.client.aclose()

    async def get_recent_chat(self, project_id: str, customer_id: str) -> list[dict[str, str]]:
        if not self._enabled:
            return []
        messages = await self.redis_store.get_recent(project_id=project_id, customer_id=customer_id)
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    async def get_long_term_facts(self, project_id: str, customer_id: str, query: str) -> list[str]:
        if not self._enabled:
            return []
        embedding = await self.openai.embed_texts([query])
        try:
            return await self.vector_store.search_customer_memories(
                project_id=project_id,
                customer_id=customer_id,
                query_vector=embedding[0],
                limit=self.settings.ltm_limit,
            )
        except Exception:
            return []

    async def post_answer(
        self,
        project_id: str,
        customer_id: str,
        user_query: str,
        assistant_answer: str,
    ) -> None:
        if not self._enabled:
            return
        await self.redis_store.append_pair(project_id=project_id, customer_id=customer_id, user_text=user_query, assistant_text=assistant_answer)

        message_inc = 2
        token_inc = estimate_tokens(user_query) + estimate_tokens(assistant_answer)
        lower = f"{user_query}\n{assistant_answer}".lower()
        has_signal = any(keyword in lower for keyword in SIGNAL_KEYWORDS)
        await self.jobs.update_customer_state(
            project_id=project_id,
            customer_id=customer_id,
            message_inc=message_inc,
            token_inc=token_inc,
            has_signal=has_signal,
        )

        if await self.jobs.should_enqueue(project_id=project_id, customer_id=customer_id):
            transcript = await self.get_recent_chat(project_id=project_id, customer_id=customer_id)
            await self.jobs.enqueue_job(project_id=project_id, customer_id=customer_id, transcript=transcript)

    async def _run_sweep_loop(self) -> None:
        while not self._stopped.is_set():
            try:
                due_customers = await self.jobs.list_due_customers()
                for project_id, customer_id in due_customers:
                    transcript = await self.get_recent_chat(project_id=project_id, customer_id=customer_id)
                    await self.jobs.enqueue_job(project_id=project_id, customer_id=customer_id, transcript=transcript)
            except Exception:
                # Keep loop alive for future iterations.
                pass
            await asyncio.sleep(self.settings.memory_periodic_sweep_seconds)

    async def _run_worker_loop(self) -> None:
        while not self._stopped.is_set():
            try:
                jobs = await self.jobs.claim_jobs()
                if not jobs:
                    await asyncio.sleep(self.settings.memory_job_poll_seconds)
                    continue
                for job in jobs:
                    await self._process_job(job.id, job.project_id, job.customer_id, job.source_window_id, job.transcript)
            except Exception:
                await asyncio.sleep(self.settings.memory_job_poll_seconds)

    async def _process_job(
        self,
        job_id: str,
        project_id: str,
        customer_id: str,
        source_window_id: str,
        transcript: list[dict[str, str]],
    ) -> None:
        try:
            facts = await self.openai.extract_facts(project_id=project_id, customer_id=customer_id, transcript=transcript)
            if not facts:
                await self.jobs.mark_done(job_id)
                return
            embeddings = await self.openai.embed_texts(facts)
            await self.vector_store.upsert_customer_memories(
                project_id=project_id,
                customer_id=customer_id,
                source_window_id=source_window_id,
                facts=facts,
                embeddings=embeddings,
            )
            await self.jobs.mark_done(job_id)
        except Exception as exc:
            await self.jobs.mark_failed(job_id=job_id, error=str(exc))


_memory_service: MemoryService | None = None


def get_memory_service() -> MemoryService:
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
