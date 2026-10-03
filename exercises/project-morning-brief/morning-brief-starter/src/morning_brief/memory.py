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
    seen_day: int
    url: str
    similarity: float

def day_int(date_iso: str) -> int:
    raise NotImplementedError

def days_before(date_iso: str, days: int) -> int:
    """yyyymmdd of `days` before the date, computed with real calendar arithmetic (not by subtracting ints)."""
    raise NotImplementedError

class StoryMemory:

    def __init__(self, path: Path | str, embedder: Embedder, name: str='story_memory') -> None:
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError

    def remember(self, date_iso: str, stories: list[tuple[str, str, str]]) -> None:
        """stories = (cluster_id, text, url). Same cluster id on the same day is an upsert."""
        raise NotImplementedError

    def follow_ups(self, date_iso: str, stories: list[tuple[str, str]], *, window_days: int=14, threshold: float=0.8) -> dict[str, FollowUp]:
        """For each (cluster_id, text) of today, the most similar story from the previous `window_days`, if above threshold."""
        raise NotImplementedError

    def prune(self, before_day: int) -> int:
        raise NotImplementedError
