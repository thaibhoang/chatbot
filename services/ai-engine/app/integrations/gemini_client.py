class GeminiClient:
    async def generate(self, query: str, contexts: list[str], use_pro: bool) -> str:
        model = "gemini-1.5-pro" if use_pro else "gemini-1.5-flash"
        joined = " | ".join(contexts)
        return f"[{model}] {query} :: {joined}"
