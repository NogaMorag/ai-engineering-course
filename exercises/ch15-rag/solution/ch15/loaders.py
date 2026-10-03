"""Chapter 15 solution: load Markdown notes into Documents (front matter stripped, content hashed)."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

FRONT_MATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.DOTALL)
HEADING = re.compile(r"^#\s+(.+)$", re.MULTILINE)
HTML_TAG = re.compile(r"</?div[^>]*>")


@dataclass(frozen=True)
class Document:
    path: str  # relative to the notes root; shown in citations
    title: str
    text: str
    content_hash: str


def strip_front_matter(text: str) -> str:
    return FRONT_MATTER.sub("", text, count=1)


def clean(text: str) -> str:
    text = strip_front_matter(text)
    text = HTML_TAG.sub("", text)  # the book's RTL/LTR wrappers carry no meaning for retrieval
    return text.strip() + "\n"


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_markdown_dir(root: Path, pattern: str = "*.md") -> list[Document]:
    documents = []
    for path in sorted(root.rglob(pattern)):
        text = clean(path.read_text(encoding="utf-8"))
        match = HEADING.search(text)
        title = match.group(1).strip() if match else path.stem
        documents.append(Document(path=path.relative_to(root).as_posix(), title=title, text=text, content_hash=content_hash(text)))
    return documents
