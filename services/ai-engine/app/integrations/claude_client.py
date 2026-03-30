from typing import AsyncIterator

from anthropic import AsyncAnthropic

from app.core.settings import get_settings


SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer from provided context only. "
    "If context is insufficient, say that clearly."
)


class ClaudeClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.client = AsyncAnthropic(api_key=settings.claude_api_key)

    async def generate(self, query: str, contexts: list[str], use_pro: bool) -> str:
        _ = use_pro
        context_text = "\n\n".join(contexts[:8])
        message = await self.client.messages.create(
            model=self.settings.claude_model,
            system=SYSTEM_PROMPT,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"Question: {query}\n\nContext:\n{context_text}",
                }
            ],
        )
        out: list[str] = []
        for block in message.content:
            text = getattr(block, "text", "")
            if text:
                out.append(text)
        return "".join(out)

    async def generate_stream(self, query: str, contexts: list[str], use_pro: bool) -> AsyncIterator[str]:
        _ = use_pro
        context_text = "\n\n".join(contexts[:8])
        async with self.client.messages.stream(
            model=self.settings.claude_model,
            system=SYSTEM_PROMPT,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"Question: {query}\n\nContext:\n{context_text}",
                }
            ],
        ) as stream:
            async for text in stream.text_stream:
                if text:
                    yield text
