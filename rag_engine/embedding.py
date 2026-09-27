"""Deterministic local embeddings used by Chroma."""
import hashlib
import math
import re


class LocalEmbeddingFunction:
    """Small offline embedding function with no model download requirement."""

    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions

    def name(self) -> str:
        return "aura_local_hash_embeddings"

    def embed_query(self, input: list[str]) -> list[list[float]]:
        return self(input)

    def __call__(self, input: list[str]) -> list[list[float]]:
        vectors = []
        for text in input:
            vector = [0.0] * self.dimensions
            for token in re.findall(r"[a-z0-9]+", text.lower()):
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:2], "big") % self.dimensions
                vector[index] += 1.0
            magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / magnitude for value in vector])
        return vectors
