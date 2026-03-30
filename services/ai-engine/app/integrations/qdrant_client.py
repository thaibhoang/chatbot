import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from app.core.settings import get_settings


class QdrantStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.client = AsyncQdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection

    async def ensure_collection(self, vector_size: int) -> None:
        collections = await self.client.get_collections()
        names = {c.name for c in collections.collections}
        if self.collection in names:
            return
        await self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    async def upsert_document(
        self,
        project_id: str,
        document_id: str,
        file_name: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> int:
        if not chunks:
            return 0
        await self.ensure_collection(len(embeddings[0]))
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid5(uuid.UUID(document_id), str(i)))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "project_id": project_id,
                        "document_id": document_id,
                        "file_name": file_name,
                        "text": chunk,
                    },
                )
            )
        await self.client.upsert(collection_name=self.collection, points=points)
        return len(points)

    async def search(self, project_id: str, query_vector: list[float], limit: int = 6) -> list[str]:
        query_filter = Filter(must=[FieldCondition(key="project_id", match=MatchValue(value=project_id))])
        if hasattr(self.client, "search"):
            hits = await self.client.search(
                collection_name=self.collection,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
            )
            return [str(hit.payload.get("text", "")) for hit in hits if hit.payload]

        result = await self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )
        points = getattr(result, "points", [])
        return [str(point.payload.get("text", "")) for point in points if getattr(point, "payload", None)]
