"""Chapter 13 starter: Reciprocal Rank Fusion. Ranks, not scores, so BM25 and cosine can be combined."""

from __future__ import annotations


def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """score(d) = sum over rankings of 1 / (k + rank_of_d), rank starting at 1. Fused list, best first."""
    # TODO: accumulate 1 / (k + rank) per id across all rankings (enumerate from 1); sort by score
    # descending and break ties by id so the result is deterministic.
    raise NotImplementedError
