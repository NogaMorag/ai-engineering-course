"""Stage 5a: same-day near-duplicate grouping with embeddings. numpy only: the day never has enough items for a database."""
from __future__ import annotations
from dataclasses import dataclass
from morning_brief.embeddings import Embedder
DEFAULT_THRESHOLD = 0.86

@dataclass
class Cluster:
    cluster_id: str
    representative_id: str
    member_ids: list[str]

def story_text(title: str, lead: str) -> str:
    """What gets embedded for grouping and for memory: the title and the first bullet."""
    raise NotImplementedError

def cluster_items(items: list[tuple[str, str]], embedder: Embedder, *, threshold: float=DEFAULT_THRESHOLD, priority: dict[str, float] | None=None) -> list[Cluster]:
    """items = (id, text). Union-find over pairs with cosine >= threshold. The representative is the highest-priority member."""
    raise NotImplementedError
