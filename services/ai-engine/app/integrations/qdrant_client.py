class QdrantStore:
    async def search(self, project_id: str, query: str) -> list[str]:
        _ = query
        # TODO: call qdrant search with project_id payload filter.
        return [f"context for {project_id}"]
