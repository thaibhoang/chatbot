import asyncio
from typing import AsyncIterator

import google.generativeai as genai

from app.core.settings import get_settings


SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer from provided context only. "
    "If context is insufficient, say that clearly."
)


class GeminiClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        genai.configure(api_key=settings.gemini_api_key)

    def _select_model(self, use_pro: bool) -> str:
        return self.settings.gemini_pro_model if use_pro else self.settings.gemini_flash_model

    async def generate(self, query: str, contexts: list[str], use_pro: bool) -> str:
        model = genai.GenerativeModel(
            model_name=self._select_model(use_pro),
            system_instruction=SYSTEM_PROMPT,
        )
        context_text = "\n\n".join(contexts[:8])
        prompt = f"Question: {query}\n\nContext:\n{context_text}"
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text or ""

    async def generate_stream(self, query: str, contexts: list[str], use_pro: bool) -> AsyncIterator[str]:
        # SDK stream iterator is synchronous, so use normal generation then yield chunks.
        answer = await self.generate(query=query, contexts=contexts, use_pro=use_pro)
        for token in answer.split(" "):
            if token:
                yield token + " "
