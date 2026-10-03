"""Chapter 12 starter: one embedding interface, a real implementation, a fake for tests, and a disk cache.

    Embedder (Protocol)   embed(texts) -> (n, d) array of L2-normalized rows
    GeminiEmbedder        gemini-embedding-2 through client.models.embed_content, batched
    FakeEmbedder          hashed character trigrams; deterministic, offline, good enough for tests
    CachedEmbedder        wraps any embedder; SQLite cache keyed by sha256(model + text)
"""

from __future__ import annotations

import hashlib
import sqlite3
import time
from pathlib import Path
from typing import Protocol

import numpy as np
from google import genai
from google.genai import types


class Embedder(Protocol):
    model: str
    dims: int

    def embed(self, texts: list[str]) -> np.ndarray: ...


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    """Scale every row to unit length so that dot product == cosine similarity."""
    matrix = np.asarray(matrix, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


class GeminiEmbedder:
    def __init__(self, model: str = "gemini-embedding-2", dims: int = 768, batch_size: int = 50, pause_s: float = 0.3) -> None:
        self.model = model
        self.dims = dims
        self.batch_size = batch_size
        self.pause_s = pause_s
        self.client = genai.Client()

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dims), dtype=np.float32)
        rows: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            response = self.client.models.embed_content(
                model=self.model,
                contents=batch,
                config=types.EmbedContentConfig(output_dimensionality=self.dims),
            )
            rows.extend(list(embedding.values or []) for embedding in response.embeddings or [])
            if start + self.batch_size < len(texts):
                time.sleep(self.pause_s)
        # gemini-embedding-2 returns unit-length vectors even at reduced dimensions (Oct 2026); other models do not, so we normalize once here and the rest of the code may assume unit length; normalize once here.
        return normalize_rows(np.array(rows, dtype=np.float32))


class FakeEmbedder:
    """Bag of hashed character trigrams. Similar strings get similar vectors; no network, no model."""

    def __init__(self, dims: int = 256, model: str = "fake-trigram-v1") -> None:
        self.model = model
        self.dims = dims

    def embed(self, texts: list[str]) -> np.ndarray:
        matrix = np.zeros((len(texts), self.dims), dtype=np.float32)
        for row, text in enumerate(texts):
            padded = f"  {text.lower()}  "
            for i in range(len(padded) - 2):
                bucket = int(hashlib.blake2b(padded[i : i + 3].encode("utf-8"), digest_size=4).hexdigest(), 16) % self.dims
                matrix[row, bucket] += 1.0
        return normalize_rows(matrix)


class CachedEmbedder:
    """Only texts that are not in the cache reach the inner embedder. Key = sha256(model, text)."""

    def __init__(self, inner: Embedder, path: Path) -> None:
        self.inner = inner
        self.model = inner.model
        self.dims = inner.dims
        self.hits = 0
        self.misses = 0
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS embeddings (key TEXT PRIMARY KEY, model TEXT NOT NULL, dims INTEGER NOT NULL, vector BLOB NOT NULL)"
        )

    @staticmethod
    def key_for(model: str, text: str) -> str:
        return hashlib.sha256(f"{model}\x00{text}".encode()).hexdigest()

    def embed(self, texts: list[str]) -> np.ndarray:
        # TODO: for each text look up key_for(self.model, text) in the table; collect the indexes that
        # are missing; count hits/misses; embed only the missing texts with self.inner; store each new
        # vector as float32 bytes (INSERT OR REPLACE) and commit; return an (n, dims) array in input order.
        raise NotImplementedError
