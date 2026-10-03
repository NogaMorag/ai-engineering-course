"""Stage 5b: cross-day story memory in Chroma. Persistence and a date filter are what justify the database here."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from morning_brief.embeddings import Embedder


@dataclass(frozen=True)
class FollowUp:
    cluster_id: str
    seen_day: int  # yyyymmdd
    url: str
    similarity: float


def day_int(date_iso: str) -> int:
    return int(date_iso.replace("-", "")[:8])


def days_before(date_iso: str, days: int) -> int:
    """yyyymmdd of `days` before the date, computed with real calendar arithmetic (not by subtracting ints)."""
    return day_int((dt.date.fromisoformat(date_iso[:10]) - dt.timedelta(days=days)).isoformat())


class StoryMemory:
    def __init__(self, path: Path | str, embedder: Embedder, name: str = "story_memory") -> None:
        self.embedder = embedder
        self.client = chromadb.PersistentClient(path=str(path), settings=ChromaSettings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(name, metadata={"hnsw:space": "cosine", "embedding_model": embedder.model})
        stored = (self.collection.metadata or {}).get("embedding_model")
        if stored != embedder.model:
            raise RuntimeError(f"story memory was built with {stored!r}; rebuild it before using {embedder.model!r}")

    def count(self) -> int:
        return self.collection.count()

    def remember(self, date_iso: str, stories: list[tuple[str, str, str]]) -> None:
        """stories = (cluster_id, text, url). Same cluster id on the same day is an upsert."""
        if not stories:
            return
        day = day_int(date_iso)
        self.collection.upsert(
            ids=[f"{day}:{cid}" for cid, _, _ in stories],
            embeddings=self.embedder.embed([t for _, t, _ in stories]).tolist(),
            documents=[t for _, t, _ in stories],
            metadatas=[{"day": day, "cluster_id": cid, "url": url} for cid, _, url in stories],
        )

    def follow_ups(self, date_iso: str, stories: list[tuple[str, str]], *, window_days: int = 14, threshold: float = 0.80) -> dict[str, FollowUp]:
        """For each (cluster_id, text) of today, the most similar story from the previous `window_days`, if above threshold."""
        if not stories or self.count() == 0:
            return {}
        today = day_int(date_iso)
        since = days_before(date_iso, window_days)
        vectors = self.embedder.embed([t for _, t in stories]).tolist()
        result = self.collection.query(query_embeddings=vectors, n_results=min(3, self.count()), where={"$and": [{"day": {"$gte": since}}, {"day": {"$lt": today}}]}, include=["metadatas", "distances"])
        found: dict[str, FollowUp] = {}
        for (cluster_id, _), metas, dists in zip(stories, result["metadatas"], result["distances"], strict=True):
            for meta, dist in zip(metas, dists, strict=True):
                similarity = 1.0 - dist
                if similarity >= threshold and (cluster_id not in found or similarity > found[cluster_id].similarity):
                    found[cluster_id] = FollowUp(cluster_id, int(meta["day"]), str(meta["url"]), round(similarity, 3))
        return found

    def prune(self, before_day: int) -> int:
        old = self.collection.get(where={"day": {"$lt": before_day}}, include=[])
        if old["ids"]:
            self.collection.delete(ids=old["ids"])
        return len(old["ids"])
