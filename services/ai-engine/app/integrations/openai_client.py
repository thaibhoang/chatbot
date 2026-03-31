from openai import AsyncOpenAI
from typing import AsyncIterator
import json

from app.core.settings import get_settings


class OpenAIClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self.client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=texts,
        )
        return [d.embedding for d in response.data]

    async def generate(
        self,
        query: str,
        contexts: list[str],
        use_pro: bool,
        model: str | None = None,
        api_key: str | None = None,
    ) -> str:
        context_text = "\n\n".join(contexts[:8])
        resolved_model = model or self.settings.openai_chat_model
        client = self.client if not api_key else AsyncOpenAI(api_key=api_key)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Answer from provided context only. "
                    "If context is insufficient, say that clearly."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {query}\n\nContext:\n{context_text}",
            },
        ]
        # use_pro kept for forward compatibility in request contract.
        _ = use_pro
        response = await client.chat.completions.create(
            model=resolved_model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    async def generate_stream(
        self,
        query: str,
        contexts: list[str],
        use_pro: bool,
        model: str | None = None,
        api_key: str | None = None,
    ) -> AsyncIterator[str]:
        context_text = "\n\n".join(contexts[:8])
        resolved_model = model or self.settings.openai_chat_model
        client = self.client if not api_key else AsyncOpenAI(api_key=api_key)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Answer from provided context only. "
                    "If context is insufficient, say that clearly."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {query}\n\nContext:\n{context_text}",
            },
        ]
        _ = use_pro
        stream = await client.chat.completions.create(
            model=resolved_model,
            messages=messages,
            temperature=0.2,
            stream=True,
        )
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def extract_facts(self, project_id: str, customer_id: str, transcript: list[dict[str, str]]) -> list[str]:
        if not transcript:
            return []
        prompt = {
            "project_id": project_id,
            "customer_id": customer_id,
            "transcript": transcript,
            "task": (
                "Extract durable customer facts only (preferences, constraints, recurring issues, profile details). "
                "Return max 8 concise facts as JSON array of strings. Exclude one-off greetings."
            ),
        }
        response = await self.client.chat.completions.create(
            model=self.settings.openai_extractor_model,
            messages=[
                {
                    "role": "system",
                    "content": "You extract long-term memory facts for CRM assistant. Output strict JSON array of strings.",
                },
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
            temperature=0.0,
        )
        raw = response.choices[0].message.content or "[]"
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            return []
        return []

