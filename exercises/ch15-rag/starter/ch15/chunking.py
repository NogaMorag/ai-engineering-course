"""Chapter 15 starter: documents -> chunks, two strategies, stable content-addressed ids."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from ch15.loaders import Document

SECTION_HEADING = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Chunk:
    id: str
    path: str
    heading: str
    text: str
    position: int


def make_chunk_id(path: str, text: str) -> str:
    """Same path + same text -> same id, on every machine, on every run. Edits change the id."""
    # TODO 1: sha256 of path + "\x00" + text, first 16 hex characters.
    raise NotImplementedError


def _cut_points(text: str, size: int, overlap: int) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            soft = text.rfind(" ", start + size // 2, end)  # prefer to cut at whitespace in the second half
            if soft != -1:
                end = soft
        spans.append((start, end))
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return spans


def chunk_fixed(doc: Document, size: int = 800, overlap: int = 100, heading: str | None = None) -> list[Chunk]:
    chunks = []
    for position, (start, end) in enumerate(_cut_points(doc.text, size, overlap)):
        piece = doc.text[start:end].strip()
        if piece:
            chunks.append(Chunk(make_chunk_id(doc.path, piece), doc.path, heading or doc.title, piece, position))
    return chunks


def chunk_by_heading(doc: Document, max_size: int = 1200, overlap: int = 100) -> list[Chunk]:
    """One chunk per Markdown section; sections longer than max_size fall back to fixed chunks."""
    matches = list(SECTION_HEADING.finditer(doc.text))
    sections: list[tuple[str, str]] = []
    if not matches or matches[0].start() > 0:
        sections.append((doc.title, doc.text[: matches[0].start() if matches else len(doc.text)]))
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(doc.text)
        sections.append((match.group(2).strip(), doc.text[match.end() : end]))

    chunks: list[Chunk] = []
    for heading, body in sections:
        body = body.strip()
        if not body:
            continue
        if len(body) <= max_size:
            chunks.append(Chunk(make_chunk_id(doc.path, body), doc.path, heading, body, len(chunks)))
        else:
            section_doc = Document(doc.path, doc.title, body, doc.content_hash)
            for piece in chunk_fixed(section_doc, size=max_size, overlap=overlap, heading=heading):
                chunks.append(Chunk(piece.id, piece.path, heading, piece.text, len(chunks)))
    return chunks


def chunk_whole_document(doc: Document) -> list[Chunk]:
    """The deliberately bad chunker used for fault injection: one chunk per file."""
    return [Chunk(make_chunk_id(doc.path, doc.text), doc.path, doc.title, doc.text.strip(), 0)]
