"""Chapter 12 solution, day 22: near-duplicate headlines at three thresholds, with a disk cache.

    uv run --env-file .env python -m ch12.near_duplicates          # first run embeds 200 texts
    uv run --env-file .env python -m ch12.near_duplicates          # second run: 200 cache hits
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from ch12.embedder import CachedEmbedder, GeminiEmbedder
from ch12.similarity import cosine_matrix, near_duplicate_pairs, threshold_sweep

DATA = Path(__file__).parent / "data" / "headlines.jsonl"
CACHE = Path(__file__).parent / "embeddings-cache.sqlite"
THRESHOLDS = (0.80, 0.85, 0.90)


def load_headlines(path: Path = DATA) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    headlines = load_headlines()
    texts = [h["text"] for h in headlines]
    embedder = CachedEmbedder(GeminiEmbedder(), CACHE)

    started = time.monotonic()
    vectors = embedder.embed(texts)
    print(f"embedded {len(texts)} headlines in {time.monotonic() - started:.1f}s  (cache hits {embedder.hits}, misses {embedder.misses})\n")

    sim = cosine_matrix(vectors)
    for threshold, count in threshold_sweep(sim, THRESHOLDS).items():
        print(f"threshold {threshold:.2f}: {count} pairs")
    print()
    for i, j, score in near_duplicate_pairs(sim, THRESHOLDS[0])[:25]:
        same_topic = headlines[i]["topic"] == headlines[j]["topic"]
        print(f"{score:.3f}  {'same-topic' if same_topic else 'CROSS-TOPIC'}\n       {texts[i]}\n       {texts[j]}")


if __name__ == "__main__":
    main()
