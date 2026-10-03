"""Chapter 13 starter: dense retrieval over a numpy matrix of normalized embeddings."""

from __future__ import annotations

import numpy as np

from ch12.embedder import Embedder


class DenseIndex:
    def __init__(self, embedder: Embedder, items: list[tuple[str, str]]) -> None:
        self.embedder = embedder
        self.ids = [item_id for item_id, _ in items]
        self.matrix = embedder.embed([text for _, text in items])

    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        scores = self.matrix @ self.embedder.embed([query])[0]
        order = np.argsort(-scores)[:k]
        return [(self.ids[int(i)], float(scores[i])) for i in order]
