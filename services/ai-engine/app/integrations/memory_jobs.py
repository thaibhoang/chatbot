import json
import uuid
from datetime import UTC, datetime, timedelta

import asyncpg

from app.core.settings import get_settings
from app.services.memory.models import CustomerMemoryJob


class MemoryJobStore:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self.pool is not None:
            return
        self.pool = await asyncpg.create_pool(dsn=self.settings.postgres_dsn, min_size=1, max_size=5)

    async def close(self) -> None:
        if self.pool is None:
            return
        await self.pool.close()
        self.pool = None

    async def update_customer_state(
        self,
        project_id: str,
        customer_id: str,
        message_inc: int,
        token_inc: int,
        has_signal: bool,
    ) -> None:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO customer_memory_states(project_id, customer_id, unsummarized_messages, unsummarized_tokens, has_signal)
                VALUES($1::uuid, $2, $3, $4, $5)
                ON CONFLICT(project_id, customer_id) DO UPDATE
                SET unsummarized_messages = customer_memory_states.unsummarized_messages + EXCLUDED.unsummarized_messages,
                    unsummarized_tokens = customer_memory_states.unsummarized_tokens + EXCLUDED.unsummarized_tokens,
                    has_signal = customer_memory_states.has_signal OR EXCLUDED.has_signal,
                    updated_at = NOW()
                """,
                project_id,
                customer_id,
                message_inc,
                token_inc,
                has_signal,
            )

    async def should_enqueue(self, project_id: str, customer_id: str) -> bool:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT unsummarized_messages, unsummarized_tokens, has_signal, last_enqueued_at
                FROM customer_memory_states
                WHERE project_id = $1::uuid AND customer_id = $2
                """,
                project_id,
                customer_id,
            )
            if row is None:
                return False
            cooldown_until = None
            if row["last_enqueued_at"] is not None:
                cooldown_until = row["last_enqueued_at"] + timedelta(minutes=self.settings.memory_trigger_cooldown_minutes)
            cooldown_ok = cooldown_until is None or cooldown_until <= datetime.now(UTC)
            threshold_hit = (
                row["unsummarized_messages"] >= self.settings.memory_trigger_message_threshold
                or row["unsummarized_tokens"] >= self.settings.memory_trigger_token_threshold
                or row["has_signal"]
            )
            return cooldown_ok and threshold_hit

    async def enqueue_job(
        self,
        project_id: str,
        customer_id: str,
        transcript: list[dict[str, str]],
    ) -> None:
        if not transcript:
            return
        assert self.pool is not None
        source_window_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{project_id}:{customer_id}:{json.dumps(transcript, sort_keys=True)}"))
        payload = {
            "project_id": project_id,
            "customer_id": customer_id,
            "transcript": transcript,
            "source_window_id": source_window_id,
        }
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO customer_memory_jobs(project_id, customer_id, source_window_id, payload, status)
                VALUES($1::uuid, $2, $3, $4::jsonb, 'pending')
                ON CONFLICT(project_id, customer_id, source_window_id) DO NOTHING
                """,
                project_id,
                customer_id,
                source_window_id,
                json.dumps(payload),
            )
            await conn.execute(
                """
                UPDATE customer_memory_states
                SET unsummarized_messages = 0,
                    unsummarized_tokens = 0,
                    has_signal = FALSE,
                    last_enqueued_at = NOW(),
                    updated_at = NOW()
                WHERE project_id = $1::uuid AND customer_id = $2
                """,
                project_id,
                customer_id,
            )

    async def list_due_customers(self) -> list[tuple[str, str]]:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT project_id::text AS project_id, customer_id
                FROM customer_memory_states
                WHERE (
                    unsummarized_messages >= $1
                    OR unsummarized_tokens >= $2
                    OR has_signal = TRUE
                )
                AND (last_enqueued_at IS NULL OR last_enqueued_at <= NOW() - make_interval(mins => $3::int))
                LIMIT $4
                """,
                self.settings.memory_trigger_message_threshold,
                self.settings.memory_trigger_token_threshold,
                self.settings.memory_trigger_cooldown_minutes,
                self.settings.memory_job_batch_size,
            )
        return [(row["project_id"], row["customer_id"]) for row in rows]

    async def claim_jobs(self) -> list[CustomerMemoryJob]:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                WITH picked AS (
                    SELECT id
                    FROM customer_memory_jobs
                    WHERE status = 'pending' AND run_at <= NOW()
                    ORDER BY created_at
                    LIMIT $1
                    FOR UPDATE SKIP LOCKED
                )
                UPDATE customer_memory_jobs
                SET status = 'running', started_at = NOW(), attempts = attempts + 1, updated_at = NOW()
                WHERE id IN (SELECT id FROM picked)
                RETURNING id::text, payload
                """,
                self.settings.memory_job_batch_size,
            )
        jobs: list[CustomerMemoryJob] = []
        for row in rows:
            payload = row["payload"]
            jobs.append(
                CustomerMemoryJob(
                    id=row["id"],
                    project_id=payload["project_id"],
                    customer_id=payload["customer_id"],
                    transcript=payload.get("transcript", []),
                    source_window_id=payload["source_window_id"],
                )
            )
        return jobs

    async def mark_done(self, job_id: str) -> None:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE customer_memory_jobs
                SET status = 'done', finished_at = NOW(), updated_at = NOW()
                WHERE id = $1::uuid
                """,
                job_id,
            )

    async def mark_failed(self, job_id: str, error: str) -> None:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT attempts, max_attempts FROM customer_memory_jobs WHERE id = $1::uuid", job_id)
            if row is None:
                return
            attempts = row["attempts"]
            max_attempts = row["max_attempts"]
            status = "dead" if attempts >= max_attempts else "pending"
            backoff_minutes = min(2**attempts, 60)
            await conn.execute(
                """
                UPDATE customer_memory_jobs
                SET status = $2,
                    last_error = $3,
                    run_at = CASE WHEN $2 = 'pending' THEN NOW() + make_interval(mins => $4::int) ELSE run_at END,
                    updated_at = NOW()
                WHERE id = $1::uuid
                """,
                job_id,
                status,
                error[:1000],
                backoff_minutes,
            )
