"""Offline tests for chapter 12. Copy to ai-course/tests/test_ch12.py and run: uv run pytest -q"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ch12.embedder import CachedEmbedder, FakeEmbedder, normalize_rows
from ch12.similarity import (
    cosine_matrix,
    mutual_nearest_neighbors,
    near_duplicate_pairs,
    nearest_neighbors,
    threshold_sweep,
)

DATA = Path(__file__).resolve().parent.parent / "ch12" / "data"


class CountingEmbedder:
    def __init__(self) -> None:
        self.inner = FakeEmbedder()
        self.model, self.dims, self.calls, self.texts_embedded = self.inner.model, self.inner.dims, 0, 0

    def embed(self, texts: list[str]) -> np.ndarray:
        self.calls += 1
        self.texts_embedded += len(texts)
        return self.inner.embed(texts)


def test_normalize_rows_and_cosine_matrix() -> None:
    m = normalize_rows(np.array([[3.0, 4.0], [0.0, 2.0], [0.0, 0.0]]))
    assert np.allclose(np.linalg.norm(m[:2], axis=1), 1.0) and np.allclose(m[2], 0.0)
    sim = cosine_matrix(m)
    assert sim.shape == (3, 3) and np.isclose(sim[0, 0], 1.0) and np.isclose(sim[0, 1], 0.8)


def test_fake_embedder_is_deterministic_and_prefers_paraphrases() -> None:
    fake = FakeEmbedder()
    a = "Cargo-Lite 2.0 ships a shared build cache that cuts compile times"
    b = "Cargo-Lite 2.0 released: shared build cache cuts compile times"
    c = "Satellite constellation photographs every hurricane from orbit"
    first, second = fake.embed([a, b, c]), fake.embed([a, b, c])
    assert np.allclose(first, second)
    sim = cosine_matrix(first)
    assert sim[0, 1] > sim[0, 2] and sim[0, 1] > 0.6


def test_nearest_neighbors_can_exclude_self() -> None:
    sim = np.array([[1.0, 0.9, 0.1], [0.9, 1.0, 0.2], [0.1, 0.2, 1.0]], dtype=np.float32)
    with_self = nearest_neighbors(sim, k=1)
    without = nearest_neighbors(sim, k=1, exclude_self=True)
    assert with_self[0][0][0] == 0 and without[0][0][0] == 1 and abs(without[0][0][1] - 0.9) < 1e-6 and without[2][0][0] == 1


def test_mutual_nearest_neighbors_requires_both_directions() -> None:
    cross = np.array([[0.9, 0.2, 0.1], [0.3, 0.8, 0.7], [0.1, 0.75, 0.6]], dtype=np.float32)
    # row 2's best column is 1, and column 1's best row is 1 -> pair 2 is not mutual
    assert mutual_nearest_neighbors(cross) == [0, 1]


def test_near_duplicate_pairs_and_threshold_sweep() -> None:
    sim = np.array([[1.0, 0.95, 0.5], [0.95, 1.0, 0.86], [0.5, 0.86, 1.0]], dtype=np.float32)
    pairs = near_duplicate_pairs(sim, 0.85)
    assert [(i, j) for i, j, _ in pairs] == [(0, 1), (1, 2)]  # each pair once, best first, no self pairs
    assert threshold_sweep(sim, (0.80, 0.90)) == {0.80: 2, 0.90: 1}


def test_cached_embedder_only_embeds_misses(tmp_path: Path) -> None:
    counting = CountingEmbedder()
    cached = CachedEmbedder(counting, tmp_path / "cache.sqlite")
    first = cached.embed(["alpha", "beta"])
    second = cached.embed(["beta", "gamma", "alpha"])
    assert counting.texts_embedded == 3 and cached.hits == 2 and cached.misses == 3
    assert np.allclose(first[1], second[0]) and np.allclose(first[0], second[2])
    reopened = CachedEmbedder(CountingEmbedder(), tmp_path / "cache.sqlite")
    assert np.allclose(reopened.embed(["gamma"])[0], second[1]) and reopened.inner.calls == 0


def test_datasets_have_the_expected_shape() -> None:
    headlines = [json.loads(line) for line in (DATA / "headlines.jsonl").read_text(encoding="utf-8").splitlines()]
    pairs = [json.loads(line) for line in (DATA / "pairs.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(headlines) == 200 and len({h["id"] for h in headlines}) == 200 and len({h["text"] for h in headlines}) == 200
    assert all(isinstance(h["day"], int) and 20260901 <= h["day"] <= 20261002 for h in headlines)
    assert len(pairs) == 10 and all(p["en"] and p["he"] for p in pairs)
