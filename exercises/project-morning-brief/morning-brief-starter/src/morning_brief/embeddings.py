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

    def embed(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError

def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    raise NotImplementedError

class GeminiEmbedder:

    def __init__(self, model: str='gemini-embedding-2', dims: int=768, batch_size: int=50) -> None:
        raise NotImplementedError

    def embed(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError

class FakeEmbedder:

    def __init__(self, dims: int=256, model: str='fake-trigram-v1') -> None:
        raise NotImplementedError

    def embed(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError

class CachedEmbedder:

    def __init__(self, inner: Embedder, path: Path | str) -> None:
        raise NotImplementedError

    def _key(self, text: str) -> str:
        raise NotImplementedError

    def embed(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError
