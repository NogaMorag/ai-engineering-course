r"""Chapter 15 starter and Checkpoint 3: ask a question over your notes, with a trace and fault injection.

    uv run --env-file .env python -m ch15.cli "מה עושה הטמפרטורה?" --notes-dir ..\book-notes\obsidian
    uv run --env-file .env python -m ch15.cli "what is RRF?" --notes-dir notes --hybrid --trace
    uv run --env-file .env python -m ch15.cli "..." --notes-dir notes --fault drop-doc --trace
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

from ch11.llm_client import GeminiClient, LLMClient
from ch12.embedder import CachedEmbedder, Embedder, GeminiEmbedder
from ch13.lexical import BM25Index
from ch15.answer import Answer, answer_question
from ch15.chunking import chunk_by_heading, chunk_fixed, chunk_whole_document
from ch15.index import NotesIndex
from ch15.loaders import Document, load_markdown_dir
from ch15.retrieve import Mode, Retriever

Fault = Literal["none", "drop-doc", "break-chunking", "ignore-context"]
CHUNKERS = {"fixed": chunk_fixed, "heading": chunk_by_heading}
DEFAULT_STORE = Path(__file__).parent / "index"
DEFAULT_NOTES = Path(__file__).parent / "data" / "sample-notes"


@dataclass
class Trace:
    question: str
    mode: str
    chunker: str
    fault: str
    documents: int
    indexed_chunks: int
    sync: dict[str, int]
    retrieved: list[dict] = field(default_factory=list)
    context_chunks: int = 0
    context_chars: int = 0
    prompt_variant: str = "grounded"
    answer: str = ""
    citations: list[int] = field(default_factory=list)
    invalid_citations: list[int] = field(default_factory=list)
    supported: bool = False
    abstained: bool = True
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    attempts: int = 0
    latency_s: float = 0.0


def drop_most_relevant(documents: list[Document], question: str) -> list[Document]:
    """Fault 'drop-doc': remove the document BM25 ranks first for the question (the one we most likely need)."""
    index = BM25Index([(d.path, d.text) for d in documents])
    hits = index.search(question, 1)
    if not hits:
        return documents[1:]
    return [d for d in documents if d.path != hits[0][0]]


def run(
    question: str,
    notes_dir: Path,
    *,
    client: LLMClient,
    embedder: Embedder,
    store_dir: Path,
    mode: Mode = "dense",
    chunker: str = "heading",
    fault: Fault = "none",
    k: int = 5,
    max_chars: int = 6000,
) -> tuple[Answer, Trace]:
    started = time.monotonic()
    documents = load_markdown_dir(notes_dir)
    if fault == "drop-doc":
        documents = drop_most_relevant(documents, question)
    chunk_fn = chunk_whole_document if fault == "break-chunking" else CHUNKERS[chunker]
    index = NotesIndex(store_dir / f"{chunker}-{fault}", embedder, chunk_fn)
    report = index.sync(documents)

    retrieved = Retriever(index, mode).retrieve(question, k)
    answer = answer_question(client, question, retrieved, max_chars=max_chars, ignore_context=(fault == "ignore-context"))

    trace = Trace(
        question=question, mode=mode, chunker=chunk_fn.__name__, fault=fault, documents=len(documents),
        indexed_chunks=index.count(), sync=report.as_dict(),
        retrieved=[{"id": r.chunk.id, "path": r.chunk.path, "heading": r.chunk.heading, "score": round(r.score, 4)} for r in retrieved],
        context_chunks=len(answer.sources), context_chars=sum(len(r.chunk.text) for r in answer.sources),
        prompt_variant="ignore-context" if fault == "ignore-context" else "grounded",
        answer=answer.text, citations=answer.citations, invalid_citations=answer.invalid_citations,
        supported=answer.supported, abstained=answer.abstained,
        latency_s=round(time.monotonic() - started, 2),
    )
    if answer.completion:
        trace.input_tokens, trace.output_tokens = answer.completion.input_tokens, answer.completion.output_tokens
        trace.cached_tokens, trace.attempts = answer.completion.cached_tokens, answer.completion.attempts
    return answer, trace


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask a question over a folder of Markdown notes.")
    parser.add_argument("question")
    parser.add_argument("--notes-dir", type=Path, default=DEFAULT_NOTES)
    parser.add_argument("--store-dir", type=Path, default=DEFAULT_STORE)
    parser.add_argument("--hybrid", action="store_true", help="BM25 + dense fused with RRF (default: dense only)")
    parser.add_argument("--chunker", choices=sorted(CHUNKERS), default="heading")
    parser.add_argument("--fault", choices=["none", "drop-doc", "break-chunking", "ignore-context"], default="none")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--trace", action="store_true", help="print the JSON trace to stderr")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.store_dir.mkdir(parents=True, exist_ok=True)
    embedder = CachedEmbedder(GeminiEmbedder(), args.store_dir / "embeddings-cache.sqlite")
    answer, trace = run(
        args.question, args.notes_dir, client=GeminiClient(), embedder=embedder, store_dir=args.store_dir,
        mode="hybrid" if args.hybrid else "dense", chunker=args.chunker, fault=args.fault, k=args.k,
    )
    print(answer.text)
    if answer.citations:
        print()
        for number in answer.citations:
            source = answer.sources[number - 1].chunk
            print(f"[{number}] {source.path} › {source.heading}")
    if answer.invalid_citations:
        print(f"\n(dropped citations that point at no source: {answer.invalid_citations})")
    if args.trace:
        print(json.dumps(asdict(trace), ensure_ascii=False, indent=1), file=sys.stderr)
    return 0 if not answer.abstained else 2


if __name__ == "__main__":
    sys.exit(main())
