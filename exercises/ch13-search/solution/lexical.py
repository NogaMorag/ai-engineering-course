"""Chapter 13 solution: lexical search with BM25 (rank-bm25) and a tokenizer that keeps identifiers."""

from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

# ascii identifiers may contain dots, dashes and underscores (3.14, e0502, cargo-lite); hebrew words are kept whole
TOKEN = re.compile(r"[a-z0-9][a-z0-9._-]*|[֐-׿]+")
HEBREW_PREFIXES = ("ו", "ה", "ב", "ל", "מ", "ש", "כ")
STOP_WORDS = frozenset(["a", "an", "the", "of", "to", "in", "on", "for", "and", "or", "with", "from", "by", "at", "as", "is", "are", "was", "were", "be", "its", "it", "this", "that"])


def tokenize(text: str) -> list[str]:
    tokens = [t.strip("._-") for t in TOKEN.findall(text.lower())]
    return [t for t in tokens if t and t not in STOP_WORDS]


def hebrew_variants(token: str) -> list[str]:
    """A Hebrew word and the same word without one leading prefix letter (ו, ה, ב, ל, מ, ש, כ)."""
    if token.startswith(HEBREW_PREFIXES) and len(token) > 3:
        return [token, token[1:]]
    return [token]


def expand_query(tokens: list[str]) -> list[str]:
    return [variant for token in tokens for variant in hebrew_variants(token)]


class BM25Index:
    def __init__(self, items: list[tuple[str, str]]) -> None:
        self.ids = [item_id for item_id, _ in items]
        self.texts = [text for _, text in items]
        self.bm25 = BM25Okapi([tokenize(text) for text in self.texts])

    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        scores = self.bm25.get_scores(expand_query(tokenize(query)))
        order = sorted(range(len(scores)), key=lambda i: -scores[i])
        return [(self.ids[i], float(scores[i])) for i in order[:k] if scores[i] > 0]
