"""Chapter 4 starter: vectors, dot product, norm, cosine similarity and ranking with numpy.

Copy to ai-course/ch04/vectors.py (with an empty ch04/__init__.py) and fill in the TODOs.
Run from the course root:

    uv run python -m ch04.vectors
"""

from __future__ import annotations

import numpy as np

Vector = list[float] | np.ndarray


def dot(a: Vector, b: Vector) -> float:
    x, y = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if x.shape != y.shape:
        raise ValueError(f"shape mismatch: {x.shape} vs {y.shape}")
    return float(x @ y)


def norm(a: Vector) -> float:
    return float(np.linalg.norm(np.asarray(a, dtype=float)))


def cosine(a: Vector, b: Vector) -> float:
    """Cosine similarity: the dot product of the two vectors after removing their lengths."""
    # TODO 1: compute both norms; raise ValueError if either is zero; return dot / (norm_a * norm_b).
    raise NotImplementedError


def normalize(a: Vector) -> np.ndarray:
    x = np.asarray(a, dtype=float)
    length = np.linalg.norm(x)
    if length == 0.0:
        raise ValueError("cannot normalize a zero vector")
    return x / length


def rank(query: Vector, documents: dict[str, Vector]) -> list[tuple[str, float]]:
    """Return (name, cosine) pairs, best match first."""
    # TODO 2: score every document with cosine(query, vector) and sort descending by score.
    raise NotImplementedError


def main() -> None:
    # Two made-up dimensions: "how much about backups", "how much about accounts".
    documents = {
        "backup policy": [3.0, 1.0],
        "login guide": [1.0, 4.0],
        "billing faq": [2.0, 2.0],
    }
    query = [1.0, 0.0]  # a question purely about backups

    print("dot products (length matters):")
    for name, vector in documents.items():
        print(f"  {name:<14} {dot(query, vector):6.3f}")

    print("cosine similarities (direction only):")
    for name, value in rank(query, documents):
        print(f"  {name:<14} {value:6.3f}")

    print()
    print("scaling a vector changes its dot product but not its cosine:")
    doubled = [6.0, 2.0]
    print(f"  dot(query, [3,1]) = {dot(query, [3.0, 1.0]):.3f}   dot(query, [6,2]) = {dot(query, doubled):.3f}")
    print(f"  cos(query, [3,1]) = {cosine(query, [3.0, 1.0]):.3f}   cos(query, [6,2]) = {cosine(query, doubled):.3f}")

    print()
    print("the same ranking as one matrix product (rows = documents):")
    matrix = np.array(list(documents.values()))  # shape (3, 2)
    unit_rows = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    scores = unit_rows @ normalize(query)  # shape (3,)
    for name, value in zip(documents, scores):
        print(f"  {name:<14} {value:6.3f}")
    print(f"  shapes: matrix {matrix.shape} @ query {normalize(query).shape} -> scores {scores.shape}")


if __name__ == "__main__":
    main()
