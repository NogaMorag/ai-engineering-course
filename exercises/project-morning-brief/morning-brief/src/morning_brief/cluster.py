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
    return f"{title}. {lead}".strip()


def cluster_items(items: list[tuple[str, str]], embedder: Embedder, *, threshold: float = DEFAULT_THRESHOLD, priority: dict[str, float] | None = None) -> list[Cluster]:
    """items = (id, text). Union-find over pairs with cosine >= threshold. The representative is the highest-priority member."""
    if not items:
        return []
    ids = [i for i, _ in items]
    vectors = embedder.embed([t for _, t in items])
    sim = vectors @ vectors.T
    parent = list(range(len(ids)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if sim[i, j] >= threshold:
                parent[find(i)] = find(j)
    groups: dict[int, list[int]] = {}
    for i in range(len(ids)):
        groups.setdefault(find(i), []).append(i)
    priority = priority or {}
    clusters = []
    for members in groups.values():
        member_ids = [ids[m] for m in members]
        representative = max(member_ids, key=lambda m: (priority.get(m, 0.0), -member_ids.index(m)))
        clusters.append(Cluster(cluster_id=f"c-{representative}", representative_id=representative, member_ids=member_ids))
    clusters.sort(key=lambda c: -priority.get(c.representative_id, 0.0))
    return clusters
