"""Chapter 12 solution, day 21: Hebrew/English sentence pairs and nearest neighbors.

    uv run --env-file .env python -m ch12.pairs_demo
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ch12.embedder import GeminiEmbedder
from ch12.similarity import cosine_matrix, mutual_nearest_neighbors, nearest_neighbors

DATA = Path(__file__).parent / "data" / "pairs.jsonl"
QUERIES = [
    "How long does compiling take now?",
    "Where does the cat nap?",
    "When is the homework due?",
    "What does temperature do in sampling?",
    "How do I get from the airport to the city?",
]


def load_pairs() -> tuple[list[str], list[str]]:
    rows = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [r["en"] for r in rows], [r["he"] for r in rows]


def main() -> None:
    english, hebrew = load_pairs()
    embedder = GeminiEmbedder()
    en_vectors = embedder.embed(english)
    he_vectors = embedder.embed(hebrew)

    cross = cosine_matrix(en_vectors, he_vectors)
    mutual = mutual_nearest_neighbors(cross)
    print(f"model {embedder.model} ({embedder.dims} dims)\n")
    print("pair  cosine(en, he)  mutual-NN  english")
    for i, sentence in enumerate(english):
        print(f"{i:>4}  {cross[i, i]:>14.3f}  {'yes' if i in mutual else 'NO ':>9}  {sentence}")
    print(f"\nmutual nearest neighbors: {len(mutual)}/{len(english)}")
    off_diagonal = cross[~np.eye(len(english), dtype=bool)]
    print(f"same-pair mean {cross.diagonal().mean():.3f} vs other-pair mean {off_diagonal.mean():.3f}\n")

    q_vectors = embedder.embed(QUERIES)
    for query, neighbors in zip(QUERIES, nearest_neighbors(cosine_matrix(q_vectors, en_vectors), k=2), strict=True):
        best, second = neighbors
        print(f"{query}\n    -> {english[best[0]]}  ({best[1]:.3f}; next {second[1]:.3f})")


if __name__ == "__main__":
    main()
