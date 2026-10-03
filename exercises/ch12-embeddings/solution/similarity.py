"""Chapter 12 solution: similarity over normalized embedding matrices (pure numpy, no network)."""

from __future__ import annotations

import numpy as np


def cosine_matrix(a: np.ndarray, b: np.ndarray | None = None) -> np.ndarray:
    """Pairwise cosine between rows of a and rows of b (or a with itself). Rows must be unit length."""
    b = a if b is None else b
    return np.asarray(a, dtype=np.float32) @ np.asarray(b, dtype=np.float32).T


def nearest_neighbors(sim: np.ndarray, k: int = 3, exclude_self: bool = False) -> list[list[tuple[int, float]]]:
    """For every row, the k highest-scoring columns as (index, score), best first."""
    sim = np.array(sim, dtype=np.float32, copy=True)
    if exclude_self:
        np.fill_diagonal(sim, -np.inf)
    result = []
    for row in sim:
        order = np.argsort(-row)[:k]
        result.append([(int(j), float(row[j])) for j in order if np.isfinite(row[j])])
    return result


def mutual_nearest_neighbors(cross: np.ndarray) -> list[int]:
    """Rows i whose best column is i AND column i's best row is i (used for sentence pairs)."""
    best_col = cross.argmax(axis=1)
    best_row = cross.argmax(axis=0)
    return [i for i in range(cross.shape[0]) if best_col[i] == i and best_row[i] == i]


def near_duplicate_pairs(sim: np.ndarray, threshold: float) -> list[tuple[int, int, float]]:
    """All pairs (i < j) with similarity >= threshold, most similar first."""
    upper = np.triu(np.ones_like(sim, dtype=bool), k=1)
    i_idx, j_idx = np.where((sim >= threshold) & upper)
    pairs = [(int(i), int(j), float(sim[i, j])) for i, j in zip(i_idx, j_idx, strict=True)]
    return sorted(pairs, key=lambda p: -p[2])


def threshold_sweep(sim: np.ndarray, thresholds: tuple[float, ...] = (0.80, 0.85, 0.90)) -> dict[float, int]:
    return {t: len(near_duplicate_pairs(sim, t)) for t in thresholds}
