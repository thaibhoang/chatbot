import json
from datetime import UTC, datetime

from redis.asyncio import Redis

from app.core.settings import get_settings
from app.services.memory.models import ChatMessage


class RedisMemoryStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.client = Redis.from_url(settings.redis_url, decode_responses=True)

    def _key(self, project_id: str, customer_id: str) -> str:
        return f"stm:{project_id}:{customer_id}"

    async def get_recent(self, project_id: str, customer_id: str) -> list[ChatMessage]:
        raw_messages = await self.client.lrange(self._key(project_id, customer_id), 0, self.settings.stm_window_size - 1)
        out: list[ChatMessage] = []
        for raw in raw_messages:
            payload = json.loads(raw)
            ts = datetime.fromisoformat(payload["ts"])
            out.append(ChatMessage(role=payload["role"], content=payload["content"], ts=ts))
        out.reverse()
        return out

    async def append_pair(self, project_id: str, customer_id: str, user_text: str, assistant_text: str) -> None:
        key = self._key(project_id, customer_id)
        now = datetime.now(UTC).isoformat()
        pipe = self.client.pipeline()
        pipe.lpush(key, json.dumps({"role": "assistant", "content": assistant_text, "ts": now}))
        pipe.lpush(key, json.dumps({"role": "user", "content": user_text, "ts": now}))
        pipe.ltrim(key, 0, self.settings.stm_window_size - 1)
        await pipe.execute()
