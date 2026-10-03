r"""Chapter 15 solution, day 29: all notes in the prompt vs retrieval, and a prompt-caching check.

    uv run --env-file .env python -m ch15.compare_long_context --notes-dir ..\book-notes\obsidian
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from ch11.llm_client import GeminiClient
from ch12.embedder import CachedEmbedder, GeminiEmbedder
from ch15.answer import (
    RESPONSE_FORMAT,
    SYSTEM_GROUNDED,
    GroundedAnswer,
    build_context,
    build_prompt,
)
from ch15.chunking import chunk_by_heading
from ch15.cli import DEFAULT_NOTES, DEFAULT_STORE
from ch15.index import NotesIndex
from ch15.loaders import load_markdown_dir
from ch15.retrieve import Retrieved, Retriever

QUESTIONS = [
    "מה עושה הטמפרטורה בזמן היצירה?",
    "What is reciprocal rank fusion and why does it use ranks?",
    "למה ניסיון חוזר בטוח רק לכשלים זמניים?",
    "What does a tool dispatcher check before running a call?",
    "מהי המשמעות של סטטוס incomplete?",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--notes-dir", type=Path, default=DEFAULT_NOTES)
    parser.add_argument("--store-dir", type=Path, default=DEFAULT_STORE)
    args = parser.parse_args()

    client = GeminiClient()
    documents = load_markdown_dir(args.notes_dir)
    embedder = CachedEmbedder(GeminiEmbedder(), args.store_dir / "embeddings-cache.sqlite")
    index = NotesIndex(args.store_dir / "heading-none", embedder, chunk_by_heading)
    index.sync(documents)
    retriever = Retriever(index, "dense")

    everything = [Retrieved(chunk, 1.0) for doc in documents for chunk in chunk_by_heading(doc)]
    long_context, _ = build_context(everything, max_chars=10**9)
    print(f"{len(documents)} notes, {len(long_context):,} characters when everything is in the prompt\n")
    print(f"{'question':<42}{'mode':<8}{'in':>7}{'cached':>8}{'out':>6}{'sec':>6}  grounded")
    for question in QUESTIONS:
        for mode in ("long", "rag"):
            if mode == "long":
                context = long_context
            else:
                context, _ = build_context(retriever.retrieve(question, 5))
            started = time.monotonic()
            completion = client.complete(build_prompt(question, context), system=SYSTEM_GROUNDED, max_output_tokens=500, temperature=0.0, response_format=RESPONSE_FORMAT)
            parsed = GroundedAnswer.model_validate_json(completion.text)
            print(f"{question[:40]:<42}{mode:<8}{completion.input_tokens:>7}{completion.cached_tokens:>8}{completion.output_tokens:>6}{time.monotonic() - started:>6.1f}  {parsed.supported}")

    print("\nprefix caching check: the same long prompt twice in a row")
    for attempt in (1, 2):
        completion = client.complete(build_prompt(QUESTIONS[0], long_context), system=SYSTEM_GROUNDED, max_output_tokens=200, temperature=0.0, response_format=RESPONSE_FORMAT)
        print(f"  call {attempt}: input {completion.input_tokens}, cached {completion.cached_tokens}")


if __name__ == "__main__":
    main()
