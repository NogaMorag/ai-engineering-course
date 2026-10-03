"""Chapter 15 solution: incremental indexing of chunks into Chroma, driven by a manifest of content hashes."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path

import chromadb
from chromadb.config import Settings

from ch12.embedder import Embedder
from ch15.chunking import Chunk
from ch15.loaders import Document

Chunker = Callable[[Document], list[Chunk]]


@dataclass
class SyncReport:
    added: int = 0
    updated: int = 0
    skipped: int = 0
    removed: int = 0
    chunks: int = 0
    embedded: int = 0

    def as_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass
class _Entry:
    content_hash: str
    chunk_ids: list[str] = field(default_factory=list)


class NotesIndex:
    def __init__(self, path: Path, embedder: Embedder, chunker: Chunker, name: str = "notes") -> None:
        self.path = Path(path)
        self.embedder = embedder
        self.chunker = chunker
        self.name = name
        self.client = chromadb.PersistentClient(path=str(self.path / "chroma"), settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(name, metadata={"hnsw:space": "cosine", "embedding_model": embedder.model})
        if (self.collection.metadata or {}).get("embedding_model") != embedder.model:
            raise RuntimeError("the index was built with another embedding model; delete the index directory and rebuild")
        self.manifest_path = self.path / f"{name}-manifest.json"
        self.manifest: dict[str, _Entry] = {
            p: _Entry(**entry) for p, entry in json.loads(self.manifest_path.read_text(encoding="utf-8")).items()
        } if self.manifest_path.exists() else {}

    def _save_manifest(self) -> None:
        self.manifest_path.write_text(json.dumps({p: asdict(e) for p, e in self.manifest.items()}, indent=1), encoding="utf-8")

    def sync(self, documents: list[Document]) -> SyncReport:
        """Index new and changed documents, drop deleted ones, skip unchanged ones. Idempotent."""
        report = SyncReport()
        present = {doc.path for doc in documents}
        for path in [p for p in self.manifest if p not in present]:
            self._delete(self.manifest.pop(path).chunk_ids)
            report.removed += 1
        for doc in documents:
            entry = self.manifest.get(doc.path)
            if entry and entry.content_hash == doc.content_hash:
                report.skipped += 1
                report.chunks += len(entry.chunk_ids)
                continue
            if entry:
                self._delete(entry.chunk_ids)
                report.updated += 1
            else:
                report.added += 1
            chunks = self.chunker(doc)
            self._upsert(chunks)
            report.embedded += len(chunks)
            report.chunks += len(chunks)
            self.manifest[doc.path] = _Entry(doc.content_hash, [c.id for c in chunks])
        self._save_manifest()
        return report

    def _delete(self, ids: list[str]) -> None:
        if ids:
            self.collection.delete(ids=ids)

    def _upsert(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        vectors = self.embedder.embed([c.text for c in chunks])
        self.collection.upsert(
            ids=[c.id for c in chunks],
            embeddings=vectors.tolist(),
            documents=[c.text for c in chunks],
            metadatas=[{"path": c.path, "heading": c.heading, "position": c.position} for c in chunks],
        )

    def count(self) -> int:
        return self.collection.count()

    def all_chunks(self) -> list[Chunk]:
        result = self.collection.get(include=["documents", "metadatas"])
        return [
            Chunk(i, m["path"], m["heading"], d, int(m["position"]))
            for i, d, m in zip(result["ids"], result["documents"], result["metadatas"], strict=True)
        ]

    def query(self, text: str, k: int = 5) -> list[tuple[Chunk, float]]:
        if self.count() == 0:
            return []
        result = self.collection.query(
            query_embeddings=self.embedder.embed([text]).tolist(),
            n_results=min(k, self.count()),
            include=["documents", "distances", "metadatas"],
        )
        return [
            (Chunk(i, m["path"], m["heading"], d, int(m["position"])), 1.0 - dist)
            for i, d, dist, m in zip(result["ids"][0], result["documents"][0], result["distances"][0], result["metadatas"][0], strict=True)
        ]
