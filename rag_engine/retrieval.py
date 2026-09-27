"""Retrieval service used by the chat endpoint."""

from .vectorbase import VectorBase


class Retriever:
    def __init__(self, vectorbase: VectorBase, count: int = 4) -> None:
        self.vectorbase = vectorbase
        self.count = count

    def retrieve(self, query: str) -> list[str]:
        return self.vectorbase.search(query, self.count)
