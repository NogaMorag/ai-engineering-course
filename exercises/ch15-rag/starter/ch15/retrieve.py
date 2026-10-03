"""Chapter 15 starter: dense or hybrid retrieval over the notes index."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ch13.hybrid import rrf
from ch13.lexical import BM25Index
from ch15.chunking import Chunk
from ch15.index import NotesIndex

Mode = Literal["dense", "hybrid"]


@dataclass(frozen=True)
class Retrieved:
    chunk: Chunk
    score: float


class Retriever:
    def __init__(self, index: NotesIndex, mode: Mode = "dense", candidates: int = 20) -> None:
        self.index = index
        self.mode = mode
        self.candidates = candidates
        self._bm25: BM25Index | None = None
        self._by_id: dict[str, Chunk] = {}

    def _lexical(self) -> BM25Index:
        if self._bm25 is None:  # built once per retriever, from whatever is in the index right now
            chunks = self.index.all_chunks()
            self._by_id = {c.id: c for c in chunks}
            self._bm25 = BM25Index([(c.id, c.text) for c in chunks])
        return self._bm25

    def retrieve(self, question: str, k: int = 5) -> list[Retrieved]:
        dense = self.index.query(question, self.candidates if self.mode == "hybrid" else k)
        if self.mode == "dense":
            return [Retrieved(chunk, score) for chunk, score in dense[:k]]
        by_id = {chunk.id: chunk for chunk, _ in dense}
        lexical = self._lexical().search(question, self.candidates)
        by_id.update({i: self._by_id[i] for i, _ in lexical if i in self._by_id})
        fused = rrf([[c.id for c, _ in dense], [i for i, _ in lexical]])
        return [Retrieved(by_id[i], score) for i, score in fused[:k] if i in by_id]
