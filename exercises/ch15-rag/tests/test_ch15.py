"""Offline tests for chapter 15. Copy to ai-course/tests/test_ch15.py and run: uv run pytest -q"""

from __future__ import annotations

import json
from pathlib import Path

from ch11.llm_client import FakeClient
from ch12.embedder import FakeEmbedder
from ch15.answer import ABSTAIN_TEXT, answer_question, build_context, build_prompt
from ch15.chunking import (
    chunk_by_heading,
    chunk_fixed,
    chunk_whole_document,
    make_chunk_id,
)
from ch15.cli import run
from ch15.index import NotesIndex
from ch15.loaders import Document, load_markdown_dir, strip_front_matter
from ch15.retrieve import Retrieved, Retriever

SAMPLE_NOTES = Path(__file__).resolve().parent.parent / "ch15" / "data" / "sample-notes"


def grounded(answer: str, citations: list[int], supported: bool = True) -> str:
    return json.dumps({"answer": answer, "citations": citations, "supported": supported})


def test_loader_strips_front_matter_and_reads_titles(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("---\ntags: [x]\n---\n<div dir=\"rtl\">\n# Title A\n\nbody\n</div>\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("no heading here\n", encoding="utf-8")
    docs = load_markdown_dir(tmp_path)
    assert [d.path for d in docs] == ["a.md", "b.md"] and docs[0].title == "Title A" and docs[1].title == "b"
    assert "---" not in docs[0].text and "<div" not in docs[0].text and len(docs[0].content_hash) == 16
    assert strip_front_matter("---\nx: 1\n---\nrest") == "rest"


def test_fixed_chunks_respect_size_overlap_and_stable_ids() -> None:
    text = " ".join(f"word{i}" for i in range(400))
    doc = Document("n.md", "N", text, "h")
    chunks = chunk_fixed(doc, size=300, overlap=50)
    assert len(chunks) > 1 and all(len(c.text) <= 300 for c in chunks)
    assert chunks[1].text[:20] in chunks[0].text  # the overlap: chunk 2 starts inside chunk 1
    assert [c.id for c in chunks] == [c.id for c in chunk_fixed(doc, size=300, overlap=50)]
    assert make_chunk_id("a.md", "same text") != make_chunk_id("b.md", "same text")


def test_heading_chunks_follow_sections_and_fall_back_when_too_long() -> None:
    text = "intro line\n\n## First\nalpha beta\n\n## Second\n" + ("gamma " * 400) + "\n"
    chunks = chunk_by_heading(Document("n.md", "N", text, "h"), max_size=500)
    assert chunks[0].heading == "N" and chunks[1].heading == "First" and chunks[1].text == "alpha beta"
    assert all(c.heading == "Second" for c in chunks[2:]) and len(chunks) > 3
    assert len(chunk_whole_document(Document("n.md", "N", text, "h"))) == 1


def test_index_sync_is_incremental(tmp_path: Path) -> None:
    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "a.md").write_text("# A\n\n## One\nalpha\n\n## Two\nbeta\n", encoding="utf-8")
    (notes / "b.md").write_text("# B\n\nbravo\n", encoding="utf-8")
    index = NotesIndex(tmp_path / "idx", FakeEmbedder(), chunk_by_heading)
    first = index.sync(load_markdown_dir(notes))
    # a.md -> 'One' + 'Two' (the empty body under '# A' is skipped), b.md -> 'B': three chunks
    assert (first.added, first.updated, first.skipped, first.removed, first.embedded) == (2, 0, 0, 0, 3) and index.count() == 3

    again = NotesIndex(tmp_path / "idx", FakeEmbedder(), chunk_by_heading).sync(load_markdown_dir(notes))
    assert (again.added, again.skipped, again.embedded) == (0, 2, 0)

    (notes / "a.md").write_text("# A\n\n## One\nalpha changed\n", encoding="utf-8")
    (notes / "b.md").unlink()
    third = NotesIndex(tmp_path / "idx", FakeEmbedder(), chunk_by_heading).sync(load_markdown_dir(notes))
    assert (third.updated, third.removed, third.added) == (1, 1, 0)
    assert index.count() == 1 and {c.heading for c in index.all_chunks()} == {"One"}


def test_dense_and_hybrid_retrieval_over_sample_notes(tmp_path: Path) -> None:
    index = NotesIndex(tmp_path / "idx", FakeEmbedder(), chunk_by_heading)
    index.sync(load_markdown_dir(SAMPLE_NOTES))
    dense = Retriever(index, "dense").retrieve("what does reciprocal rank fusion sum?", k=2)
    assert dense[0].chunk.path == "fusion.md"
    hybrid = Retriever(index, "hybrid").retrieve("E0502", k=3)
    assert hybrid[0].chunk.path == "retries.md" and 0 < hybrid[0].score < 0.1  # rrf scores are ~1/(60+rank)


def test_build_context_numbers_sources_and_respects_the_budget() -> None:
    items = [Retrieved(c, 1.0) for c in chunk_fixed(Document("n.md", "N", "x" * 1000, "h"), size=300, overlap=0)]
    context, included = build_context(items, max_chars=700)
    assert len(included) == 2 and context.startswith("[1] (n.md › N)") and "[3]" not in context
    assert build_prompt("q?", context).endswith("<question>\nq?\n</question>")
    assert build_context([], max_chars=10) == ("", [])


def test_answer_validates_citations_and_abstains() -> None:
    items = [Retrieved(c, 1.0) for c in chunk_by_heading(load_markdown_dir(SAMPLE_NOTES)[0])]
    fake = FakeClient(script=[grounded("RRF sums 1/(k+rank). [1][7]", [1, 7]), grounded("", [], supported=False), "not json"])
    first = answer_question(fake, "what does RRF sum?", items)
    assert not first.abstained and first.citations == [1] and first.invalid_citations == [7]
    assert fake.calls[0]["system"].startswith("You answer questions from a personal knowledge base")
    second = answer_question(fake, "who won the 1998 world cup?", items)
    assert second.abstained and second.text == ABSTAIN_TEXT and second.citations == []
    third = answer_question(fake, "q", items)
    assert third.abstained and third.raw == "not json"
    assert answer_question(fake, "q", []).abstained and len(fake.calls) == 3


def test_run_records_a_trace_and_faults_are_visible_in_it(tmp_path: Path) -> None:
    def ask(fault: str, script: list[str]) -> tuple:
        return run(
            "which failures are safe to retry?", SAMPLE_NOTES, client=FakeClient(script=script), embedder=FakeEmbedder(),
            store_dir=tmp_path, mode="hybrid", chunker="heading", fault=fault, k=3,
        )

    answer, trace = ask("none", [grounded("Only transient failures. [1]", [1])])
    assert trace.documents == 3 and trace.indexed_chunks == 6 and trace.retrieved[0]["path"] == "retries.md"
    assert not answer.abstained and trace.citations == [1] and trace.prompt_variant == "grounded"

    _, dropped = ask("drop-doc", [grounded("", [], supported=False)])
    assert dropped.documents == 2 and all(r["path"] != "retries.md" for r in dropped.retrieved) and dropped.abstained

    _, broken = ask("break-chunking", [grounded("Only transient failures. [1]", [1])])
    assert broken.indexed_chunks == 3 and broken.chunker == "chunk_whole_document"

    _, ignored = ask("ignore-context", [grounded("Everything, always.", [], supported=True)])
    assert ignored.prompt_variant == "ignore-context" and ignored.abstained  # no valid citation -> abstain
