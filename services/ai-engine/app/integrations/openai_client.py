from openai import AsyncOpenAI

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

    async def generate(self, query: str, contexts: list[str], use_pro: bool) -> str:
        context_text = "\n\n".join(contexts[:8])
        model = self.settings.openai_chat_model
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
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

