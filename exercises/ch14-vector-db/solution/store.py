"""Chapter 14 solution: the headline index in Chroma, with metadata filters and a reindex on model change.

    uv run --env-file .env python -m ch14.store
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb
import numpy as np
from chromadb.config import Settings

from ch12.embedder import CachedEmbedder, Embedder, GeminiEmbedder
from ch12.near_duplicates import load_headlines

STORE_DIR = Path(__file__).parent / "chroma"
CACHE = Path(__file__).resolve().parent.parent / "ch12" / "embeddings-cache.sqlite"


@dataclass(frozen=True)
class Headline:
    id: str
    text: str
    source: str
    day: int  # yyyymmdd as an integer: Chroma compares numbers with $gte, not date strings


@dataclass(frozen=True)
class Hit:
    id: str
    text: str
    score: float  # cosine similarity (Chroma returns cosine *distance* = 1 - similarity)
    metadata: dict[str, Any]


class HeadlineStore:
    """One collection, embeddings computed by us, the embedding model name recorded in the collection metadata."""

    def __init__(self, path: Path, embedder: Embedder, name: str = "headlines") -> None:
        self.embedder = embedder
        self.name = name
        self.client = chromadb.PersistentClient(path=str(path), settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(
            name, metadata={"hnsw:space": "cosine", "embedding_model": embedder.model}
        )

    @property
    def stored_model(self) -> str | None:
        return (self.collection.metadata or {}).get("embedding_model")

    def needs_reindex(self) -> bool:
        return self.stored_model != self.embedder.model

    def upsert(self, items: list[Headline], batch_size: int = 100) -> None:
        if self.needs_reindex():
            raise RuntimeError(f"collection was built with {self.stored_model!r}; call reindex() before adding {self.embedder.model!r} vectors")
        for start in range(0, len(items), batch_size):
            batch = items[start : start + batch_size]
            vectors = self.embedder.embed([h.text for h in batch])
            self.collection.upsert(
                ids=[h.id for h in batch],
                embeddings=vectors.tolist(),
                documents=[h.text for h in batch],
                metadatas=[{"source": h.source, "day": h.day} for h in batch],
            )

    def search(self, query: str, k: int = 5, *, since_day: int | None = None, source: str | None = None) -> list[Hit]:
        clauses: list[dict[str, Any]] = []
        if since_day is not None:
            clauses.append({"day": {"$gte": since_day}})
        if source is not None:
            clauses.append({"source": source})
        where = None if not clauses else clauses[0] if len(clauses) == 1 else {"$and": clauses}
        result = self.collection.query(
            query_embeddings=self.embedder.embed([query]).tolist(),
            n_results=min(k, max(self.count(), 1)),
            where=where,
            include=["documents", "distances", "metadatas"],
        )
        return [
            Hit(id=i, text=doc, score=1.0 - dist, metadata=meta or {})
            for i, doc, dist, meta in zip(result["ids"][0], result["documents"][0], result["distances"][0], result["metadatas"][0], strict=True)
        ]

    def count(self) -> int:
        return self.collection.count()

    def reindex(self, items: list[Headline]) -> None:
        """Drop everything and rebuild with the current embedder. Vectors from two models never mix."""
        self.client.delete_collection(self.name)
        self.collection = self.client.get_or_create_collection(
            self.name, metadata={"hnsw:space": "cosine", "embedding_model": self.embedder.model}
        )
        self.upsert(items)


def numpy_search(embedder: Embedder, items: list[Headline], query: str, k: int = 5) -> list[tuple[str, float]]:
    """The 'is numpy enough?' baseline: a full scan over all vectors."""
    matrix = embedder.embed([h.text for h in items])
    scores = matrix @ embedder.embed([query])[0]
    order = np.argsort(-scores)[:k]
    return [(items[int(i)].id, float(scores[i])) for i in order]


def main() -> None:
    items = [Headline(h["id"], h["text"], h["source"], h["day"]) for h in load_headlines()]
    embedder = CachedEmbedder(GeminiEmbedder(), CACHE)
    store = HeadlineStore(STORE_DIR, embedder)
    if store.needs_reindex():
        print(f"model changed ({store.stored_model} -> {embedder.model}); reindexing")
        store.reindex(items)
    else:
        started = time.monotonic()
        store.upsert(items)
        print(f"upserted {len(items)} headlines in {time.monotonic() - started:.1f}s (count={store.count()})")

    query = "kubernetes upgrade broke the network"
    print(f"\nquery: {query}")
    print("chroma top-5:  ", [(h.id, round(h.score, 3)) for h in store.search(query, 5)])
    print("numpy  top-5:  ", [(i, round(s, 3)) for i, s in numpy_search(embedder, items, query, 5)])
    print("since 20260920:", [(h.id, h.metadata["day"]) for h in store.search(query, 5, since_day=20260920)])
    print("source=hn:     ", [(h.id, h.metadata["source"]) for h in store.search(query, 5, source="hn")])

    print("\nsimulating a model change: a store opened with another embedder model refuses to mix vectors")
    other = CachedEmbedder(GeminiEmbedder(dims=256), CACHE)
    other.model = other.inner.model = "gemini-embedding-2@256"
    store_b = HeadlineStore(STORE_DIR, other)
    print("needs_reindex:", store_b.needs_reindex())
    try:
        store_b.upsert(items[:1])
    except RuntimeError as err:
        print("upsert refused:", err)


if __name__ == "__main__":
    main()
