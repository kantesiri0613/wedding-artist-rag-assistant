"""Chroma-backed vector database management."""

from pathlib import Path
from typing import Any

import chromadb

from .embedding import LocalEmbeddingFunction


class VectorBase:
    """Own the persistent Chroma collection and its indexing/query operations."""

    def __init__(self, database_dir: Path, collection_name: str) -> None:
        self.database_dir = database_dir
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=str(database_dir))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=LocalEmbeddingFunction(),
        )

    def index(self, chunks: list[str], source_name: str) -> int:
        """Upsert current chunks so edits to the knowledge base are reflected."""
        ids = [f"live-painting-{index}" for index in range(len(chunks))]
        if ids:
            self.collection.upsert(
                ids=ids,
                documents=chunks,
                metadatas=[{"source": source_name} for _ in chunks],
            )
        return len(chunks)

    def search(self, query: str, count: int = 4) -> list[str]:
        """Return the nearest knowledge-base documents for a query."""
        if self.collection.count() == 0:
            return []
        result: dict[str, Any] = self.collection.query(
            query_texts=[query],
            n_results=min(count, self.collection.count()),
        )
        documents = result.get("documents", [[]])
        return documents[0] if documents else []
