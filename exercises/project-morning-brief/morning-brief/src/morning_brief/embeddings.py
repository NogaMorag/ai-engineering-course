"""Embeddings: one interface, the Gemini model, a fake for tests, and a SQLite cache keyed by model + text."""

from __future__ import annotations

import hashlib
import sqlite3
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
    matrix = np.asarray(matrix, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


class GeminiEmbedder:
    def __init__(self, model: str = "gemini-embedding-2", dims: int = 768, batch_size: int = 50) -> None:
        self.model, self.dims, self.batch_size = model, dims, batch_size
        self.client = genai.Client()

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dims), dtype=np.float32)
        rows = []
        for start in range(0, len(texts), self.batch_size):
            response = self.client.models.embed_content(model=self.model, contents=texts[start : start + self.batch_size], config=types.EmbedContentConfig(output_dimensionality=self.dims))
            rows.extend(list(e.values or []) for e in response.embeddings or [])
        return normalize_rows(np.array(rows, dtype=np.float32))


class FakeEmbedder:
    def __init__(self, dims: int = 256, model: str = "fake-trigram-v1") -> None:
        self.model, self.dims = model, dims

    def embed(self, texts: list[str]) -> np.ndarray:
        matrix = np.zeros((len(texts), self.dims), dtype=np.float32)
        for row, text in enumerate(texts):
            padded = f"  {text.lower()}  "
            for i in range(len(padded) - 2):
                matrix[row, int(hashlib.blake2b(padded[i : i + 3].encode(), digest_size=4).hexdigest(), 16) % self.dims] += 1.0
        return normalize_rows(matrix)


class CachedEmbedder:
    def __init__(self, inner: Embedder, path: Path | str) -> None:
        self.inner, self.model, self.dims = inner, inner.model, inner.dims
        self.hits = self.misses = 0
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.execute("CREATE TABLE IF NOT EXISTS embeddings (key TEXT PRIMARY KEY, model TEXT NOT NULL, dims INTEGER NOT NULL, vector BLOB NOT NULL)")

    def _key(self, text: str) -> str:
        return hashlib.sha256(f"{self.model}\x00{text}".encode()).hexdigest()

    def embed(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dims), dtype=np.float32)
        missing = []
        for i, text in enumerate(texts):
            row = self.conn.execute("SELECT vector FROM embeddings WHERE key = ?", (self._key(text),)).fetchone()
            if row is None:
                missing.append(i)
            else:
                out[i] = np.frombuffer(row[0], dtype=np.float32)
        self.hits += len(texts) - len(missing)
        self.misses += len(missing)
        if missing:
            fresh = self.inner.embed([texts[i] for i in missing])
            for i, vector in zip(missing, fresh, strict=True):
                out[i] = vector
                self.conn.execute("INSERT OR REPLACE INTO embeddings (key, model, dims, vector) VALUES (?,?,?,?)", (self._key(texts[i]), self.model, self.dims, vector.astype(np.float32).tobytes()))
            self.conn.commit()
        return out
