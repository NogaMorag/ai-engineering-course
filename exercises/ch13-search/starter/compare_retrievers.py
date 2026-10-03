"""Chapter 13 starter, days 23-25: BM25 vs dense vs hybrid vs hybrid + rerank on 20 labeled queries.

    uv run --env-file .env python -m ch13.compare_retrievers
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from ch11.llm_client import GeminiClient
from ch12.embedder import CachedEmbedder, GeminiEmbedder
from ch12.near_duplicates import load_headlines
from ch13.dense import DenseIndex
from ch13.hybrid import rrf
from ch13.lexical import BM25Index
from ch13.metrics import evaluate
from ch13.rerank import LLMReranker

QUERIES = Path(__file__).parent / "data" / "queries.jsonl"
CACHE = Path(__file__).resolve().parent.parent / "ch12" / "embeddings-cache.sqlite"
CANDIDATES = 20


def load_queries(path: Path = QUERIES) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    headlines = load_headlines()
    items = [(h["id"], h["text"]) for h in headlines]
    text_of = dict(items)
    queries = load_queries()
    labels = {q["id"]: set(q["relevant"]) for q in queries}

    embedder = CachedEmbedder(GeminiEmbedder(), CACHE)
    bm25 = BM25Index(items)
    dense = DenseIndex(embedder, items)
    reranker = LLMReranker(GeminiClient())

    runs: dict[str, dict[str, list[str]]] = {"bm25": {}, "dense": {}, "hybrid": {}, "hybrid+rerank": {}}
    timings: dict[str, float] = dict.fromkeys(runs, 0.0)
    for q in queries:
        t0 = time.monotonic()
        lexical = [i for i, _ in bm25.search(q["query"], CANDIDATES)]
        t1 = time.monotonic()
        semantic = [i for i, _ in dense.search(q["query"], CANDIDATES)]
        t2 = time.monotonic()
        fused = [i for i, _ in rrf([lexical, semantic])]
        t3 = time.monotonic()
        reranked = [i for i, _ in reranker.rerank(q["query"], [(i, text_of[i]) for i in fused[:CANDIDATES]], top_n=5)]
        t4 = time.monotonic()
        runs["bm25"][q["id"]], runs["dense"][q["id"]], runs["hybrid"][q["id"]], runs["hybrid+rerank"][q["id"]] = lexical, semantic, fused, reranked
        timings["bm25"] += t1 - t0
        timings["dense"] += t2 - t1
        timings["hybrid"] += t3 - t2
        timings["hybrid+rerank"] += t4 - t3

    print(f"{'retriever':<15}{'hit@3':>8}{'recall@5':>10}{'mrr':>8}{'sec/query':>12}")
    for name, run in runs.items():
        m = evaluate(run, labels)
        print(f"{name:<15}{m['hit@3']:>8.2f}{m['recall@5']:>10.2f}{m['mrr']:>8.2f}{timings[name] / len(queries):>12.2f}")

    print("\nwhere they disagree (top-1):")
    for q in queries:
        tops = {name: (run[q['id']][0] if run[q['id']] else "-") for name, run in runs.items()}
        if len(set(tops.values())) > 1:
            marks = "  ".join(f"{name}={top}{'*' if top in labels[q['id']] else ''}" for name, top in tops.items())
            print(f"  {q['query'][:45]:<45} {marks}")
    print("\n* = relevant. Embedding cache hits/misses:", embedder.hits, embedder.misses)


if __name__ == "__main__":
    main()
