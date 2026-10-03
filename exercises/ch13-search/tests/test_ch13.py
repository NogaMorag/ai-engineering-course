"""Offline tests for chapter 13. Copy to ai-course/tests/test_ch13.py and run: uv run pytest -q"""

from __future__ import annotations

import json
from pathlib import Path

from ch11.llm_client import FakeClient
from ch12.embedder import FakeEmbedder
from ch13.dense import DenseIndex
from ch13.hybrid import rrf
from ch13.lexical import BM25Index, expand_query, hebrew_variants, tokenize
from ch13.metrics import (
    evaluate,
    hit_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)
from ch13.rerank import LLMReranker

DATA = Path(__file__).resolve().parent.parent
ITEMS = [
    ("h1", "Rust compiler error E0502 explained: the borrow checker and mutable references"),
    ("h2", "Python 3.14 released with the free-threaded build enabled by default"),
    ("h3", "Kubernetes 1.36 upgrade breaks pod networking for legacy CNI clusters"),
    ("h4", "Satellite constellation photographs every hurricane from orbit"),
]


def test_tokenize_keeps_identifiers_and_drops_stop_words() -> None:
    assert tokenize("Error E0502 in the Rust compiler") == ["error", "e0502", "rust", "compiler"]
    assert tokenize("Python 3.14 and Cargo-Lite 2.0.") == ["python", "3.14", "cargo-lite", "2.0"]
    assert tokenize("שדרוג קוברנטיס שבר את הרשת") == ["שדרוג", "קוברנטיס", "שבר", "את", "הרשת"]


def test_hebrew_variants_and_query_expansion() -> None:
    assert hebrew_variants("הרשת") == ["הרשת", "רשת"]
    assert hebrew_variants("את") == ["את"]
    assert expand_query(["הרשת", "rust"]) == ["הרשת", "רשת", "rust"]


def test_bm25_finds_the_identifier_and_returns_nothing_for_unknown_terms() -> None:
    index = BM25Index(ITEMS)
    assert index.search("E0502", k=3)[0][0] == "h1"
    assert index.search("kubernetes networking", k=1)[0][0] == "h3"
    assert index.search("zebra quantum", k=3) == []


def test_dense_index_ranks_the_paraphrase_first() -> None:
    index = DenseIndex(FakeEmbedder(), ITEMS)
    assert index.search("Kubernetes 1.36 upgrade broke pod networking", k=1)[0][0] == "h3"
    assert len(index.search("anything", k=10)) == 4


def test_rrf_sums_reciprocal_ranks_and_breaks_ties_by_id() -> None:
    fused = rrf([["a", "b", "c"], ["b", "a", "d"]], k=60)
    scores = dict(fused)
    assert fused[0][0] in {"a", "b"} and abs(scores["a"] - scores["b"]) < 1e-9 and fused[0][0] == "a"
    assert abs(scores["a"] - (1 / 61 + 1 / 62)) < 1e-9 and abs(scores["d"] - 1 / 63) < 1e-9
    assert [i for i, _ in fused][-2:] == ["c", "d"]  # both 1/63: the tie is broken by id


def test_retrieval_metrics() -> None:
    ranked, relevant = ["x", "h1", "y", "h2"], {"h1", "h2", "h3"}
    assert hit_at_k(ranked, relevant, 1) == 0.0 and hit_at_k(ranked, relevant, 2) == 1.0
    assert abs(recall_at_k(ranked, relevant, 4) - 2 / 3) < 1e-9 and recall_at_k(ranked, set(), 4) == 0.0
    assert precision_at_k(ranked, relevant, 4) == 0.5
    assert reciprocal_rank(ranked, relevant) == 0.5 and reciprocal_rank(["x"], relevant) == 0.0
    result = evaluate({"q1": ranked, "q2": ["h3"]}, {"q1": relevant, "q2": {"h3"}}, ks=(1,))
    assert result == {"hit@1": 0.5, "recall@1": round((0 + 1) / 2, 3), "mrr": 0.75}


def test_reranker_scores_known_ids_and_defaults_missing_ones_to_zero() -> None:
    fake = FakeClient(script=[json.dumps({"scores": [{"id": "h3", "score": 9}, {"id": "h1", "score": 4}, {"id": "ghost", "score": 10}]})])
    ranked = LLMReranker(fake).rerank("kubernetes networking", ITEMS, top_n=3)
    assert [i for i, _ in ranked] == ["h3", "h1", "h2"]  # h2/h4 missing -> 0, input order keeps h2 before h4
    assert fake.calls[0]["response_format"] is not None and "<query>" in fake.calls[0]["prompt"]
    assert LLMReranker(fake).rerank("q", [], top_n=3) == []


def test_labeled_queries_reference_existing_headlines() -> None:
    headlines = {json.loads(l)["id"] for l in (DATA / "ch12" / "data" / "headlines.jsonl").read_text(encoding="utf-8").splitlines()}
    queries = [json.loads(l) for l in (DATA / "ch13" / "data" / "queries.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(queries) == 20 and all(q["relevant"] and set(q["relevant"]) <= headlines for q in queries)
