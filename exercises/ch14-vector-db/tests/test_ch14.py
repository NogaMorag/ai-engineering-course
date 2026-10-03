"""Offline tests for chapter 14. Copy to ai-course/tests/test_ch14.py and run: uv run pytest -q"""

from __future__ import annotations

from pathlib import Path

import pytest

from ch12.embedder import FakeEmbedder
from ch14.store import Headline, HeadlineStore, numpy_search

ITEMS = [
    Headline("h1", "Rust compiler error E0502 explained: the borrow checker and mutable references", "devwire", 20260905),
    Headline("h2", "Python 3.14 released with the free-threaded build enabled by default", "hn", 20260912),
    Headline("h3", "Kubernetes 1.36 upgrade breaks pod networking for legacy CNI clusters", "cloudbeat", 20260925),
    Headline("h4", "Clusters on the legacy CNI plugin lose pod networking after upgrading to Kubernetes 1.36", "hn", 20261001),
]


@pytest.fixture
def store(tmp_path: Path) -> HeadlineStore:
    s = HeadlineStore(tmp_path / "chroma", FakeEmbedder())
    s.upsert(ITEMS)
    return s


def test_upsert_search_and_metadata_filters(store: HeadlineStore) -> None:
    assert store.count() == 4
    hits = store.search("kubernetes upgrade broke networking", k=2)
    assert {h.id for h in hits} == {"h3", "h4"} and all(0.0 <= h.score <= 1.0 for h in hits)
    assert {h.id for h in store.search("kubernetes networking", k=4, since_day=20260920)} == {"h3", "h4"}
    assert [h.id for h in store.search("kubernetes networking", k=4, since_day=20260920, source="hn")] == ["h4"]
    assert len(store.search("anything", k=10)) == 4  # k larger than the collection is clamped


def test_chroma_agrees_with_the_numpy_scan(store: HeadlineStore) -> None:
    query = "free-threaded python release"
    chroma_ids = [h.id for h in store.search(query, k=3)]
    numpy_ids = [i for i, _ in numpy_search(FakeEmbedder(), ITEMS, query, k=3)]
    assert chroma_ids == numpy_ids


def test_upsert_is_idempotent_and_updates_in_place(store: HeadlineStore) -> None:
    store.upsert(ITEMS)
    assert store.count() == 4
    store.upsert([Headline("h2", "Python 3.14 released: free threading is now the default", "hn", 20260912)])
    assert store.count() == 4 and store.search("python 3.14 free threading", k=1)[0].text.endswith("default")


def test_model_change_is_refused_until_reindex(tmp_path: Path) -> None:
    HeadlineStore(tmp_path / "chroma", FakeEmbedder()).upsert(ITEMS)
    other = HeadlineStore(tmp_path / "chroma", FakeEmbedder(dims=128, model="fake-trigram-v2"))
    assert other.needs_reindex() and other.stored_model == "fake-trigram-v1"
    with pytest.raises(RuntimeError):
        other.upsert(ITEMS[:1])
    other.reindex(ITEMS)
    assert not other.needs_reindex() and other.stored_model == "fake-trigram-v2" and other.count() == 4
