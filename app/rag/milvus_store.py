"""Optional Milvus vector repository.

PostgreSQL/pgvector remains the default. Set ``VECTOR_STORE_BACKEND=milvus``
and install ``pymilvus`` to use this adapter; document metadata continues to
be persisted in PostgreSQL so existing APIs and migrations remain compatible.
"""
import asyncio
import uuid

from app.core.config import get_settings
from app.rag.models import DocumentChunk, SearchResult


class MilvusVectorRepository:
    def __init__(self):
        try:
            from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility
        except ImportError as exc:
            raise RuntimeError("VECTOR_STORE_BACKEND=milvus requires pymilvus>=2.4") from exc
        self._Collection = Collection
        self._DataType = DataType
        self._connections = connections
        self._utility = utility
        self.settings = get_settings()
        self._connections.connect(alias="default", uri=self.settings.milvus_uri)
        self.collection = self._ensure_collection(CollectionSchema, FieldSchema)

    def _ensure_collection(self, CollectionSchema, FieldSchema):
        name = self.settings.milvus_collection
        if self._utility.has_collection(name):
            collection = self._Collection(name)
        else:
            schema = CollectionSchema(fields=[
                FieldSchema("id", self._DataType.VARCHAR, is_primary=True, max_length=64),
                FieldSchema("knowledge_base_id", self._DataType.VARCHAR, max_length=64),
                FieldSchema("tenant_id", self._DataType.VARCHAR, max_length=64),
                FieldSchema("document_id", self._DataType.VARCHAR, max_length=64),
                FieldSchema("chunk_index", self._DataType.INT64),
                FieldSchema("content", self._DataType.VARCHAR, max_length=65535),
                FieldSchema("embedding", self._DataType.FLOAT_VECTOR, dim=self.settings.embedding_dimensions),
            ], description="Enterprise RAG document chunks")
            collection = self._Collection(name, schema=schema)
            collection.create_index("embedding", {"index_type": "HNSW", "metric_type": "COSINE", "params": {"M": 16, "efConstruction": 200}})
        collection.load()
        return collection

    async def insert(self, *, knowledge_base_id: uuid.UUID, tenant_id: str, chunks: list[dict]) -> None:
        rows = [[str(item["id"]) for item in chunks], [str(knowledge_base_id)] * len(chunks), [tenant_id] * len(chunks), [str(item["document_id"]) for item in chunks], [item["chunk_index"] for item in chunks], [item["content"] for item in chunks], [item["embedding"] for item in chunks]]
        await asyncio.to_thread(self.collection.insert, rows)
        await asyncio.to_thread(self.collection.flush)

    async def search(self, *, knowledge_base_id: uuid.UUID, query_embedding: list[float], top_k: int = 5, tenant_id: str | None = None) -> list[SearchResult]:
        expr = f'knowledge_base_id == "{knowledge_base_id}"'
        if tenant_id:
            expr += f' and tenant_id == "{tenant_id}"'
        result = await asyncio.to_thread(self.collection.search, [query_embedding], "embedding", {"metric_type": "COSINE", "params": {"ef": max(64, top_k * 4)}}, limit=top_k, expr=expr, output_fields=["id", "tenant_id", "document_id", "chunk_index", "content"])
        items: list[SearchResult] = []
        for hit in result[0]:
            entity = hit.entity
            chunk = DocumentChunk(id=str(entity.get("id", hit.id)), tenant_id=entity.get("tenant_id", tenant_id or "default"), document_id=entity.get("document_id", ""), chunk_index=int(entity.get("chunk_index", -1)), content=entity.get("content", ""), metadata={"chunk_index": int(entity.get("chunk_index", -1))})
            items.append(SearchResult(chunk=chunk, score=float(hit.distance)))
        return items
