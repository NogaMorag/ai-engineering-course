"""Chapter 13 solution: retrieval metrics. Pure functions; `relevant` is the labeled set for one query."""

from __future__ import annotations

from collections.abc import Iterable


def hit_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    return 1.0 if any(item in relevant for item in ranked[:k]) else 0.0


def recall_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(ranked[:k]) & relevant) / len(relevant)


def precision_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        return 0.0
    return len(set(ranked[:k]) & relevant) / k


def reciprocal_rank(ranked: list[str], relevant: set[str]) -> float:
    for position, item in enumerate(ranked, start=1):
        if item in relevant:
            return 1.0 / position
    return 0.0


def evaluate(run: dict[str, list[str]], labels: dict[str, set[str]], ks: Iterable[int] = (3, 5)) -> dict[str, float]:
    """Mean metrics over all labeled queries. `run` maps query id -> ranked ids."""
    ks = tuple(ks)
    totals: dict[str, float] = {f"hit@{k}": 0.0 for k in ks} | {f"recall@{k}": 0.0 for k in ks} | {"mrr": 0.0}
    for query_id, relevant in labels.items():
        ranked = run.get(query_id, [])
        for k in ks:
            totals[f"hit@{k}"] += hit_at_k(ranked, relevant, k)
            totals[f"recall@{k}"] += recall_at_k(ranked, relevant, k)
        totals["mrr"] += reciprocal_rank(ranked, relevant)
    n = max(len(labels), 1)
    return {name: round(value / n, 3) for name, value in totals.items()}
