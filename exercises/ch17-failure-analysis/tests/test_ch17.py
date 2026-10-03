"""Offline tests for chapter 17. Copy to ai-course/tests/test_ch17.py and run: uv run pytest -q"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from ch16.cases import Case, Expectation
from ch17.analyze import (
    append_regressions,
    prioritize,
    regression_cases,
    render_analysis,
    rollup,
    tag_records,
)
from ch17.taxonomy import TAXONOMY, classify


def case(cid: str, *, answerable: bool = True, sources=("retries.md",), mention=("transient",), forbid=()) -> Case:
    return Case(id=cid, question="q", category="direct", group=cid, split="dev",
                expected=Expectation(answerable=answerable, must_mention_any=list(mention), must_not_mention=list(forbid), source_paths=list(sources), reference=""))


def record(cid: str, *, passed=False, abstained=False, retrieved=(), context=(), cited=(), invalid=(), failed_checks=()) -> dict:
    checks = [{"name": name, "passed": name not in failed_checks, "detail": ""} for name in ("abstention", "no_fabricated_citation", "has_citation", "mentions_key_fact", "no_forbidden_content", "cites_expected_source", "language_matches")]
    return {"case_id": cid, "category": "direct", "question": "q", "passed": passed, "abstained": abstained, "retrieved_paths": list(retrieved), "context_paths": list(context), "cited_paths": list(cited), "invalid_citations": list(invalid), "checks": checks}


def test_classify_by_stage() -> None:
    assert classify(record("p", passed=True), case("p")) == []
    assert classify(record("a", abstained=True, retrieved=["fusion.md"], context=["fusion.md"], failed_checks=["abstention"]), case("a")) == ["retrieval_miss"]
    assert classify(record("b", abstained=True, retrieved=["retries.md", "fusion.md"], context=["fusion.md"], failed_checks=["abstention"]), case("b")) == ["context_truncated"]
    assert classify(record("c", abstained=True, retrieved=["retries.md"], context=["retries.md"], failed_checks=["abstention"]), case("c")) == ["over_refusal"]
    assert classify(record("d", retrieved=["retries.md"], context=["retries.md"], cited=["retries.md"], failed_checks=["mentions_key_fact"]), case("d")) == ["missing_key_fact"]
    assert classify(record("e", retrieved=["retries.md"], context=["retries.md"], cited=["fusion.md"], failed_checks=["cites_expected_source"]), case("e")) == ["wrong_source_cited"]
    assert classify(record("f", retrieved=["retries.md"], context=["retries.md"], failed_checks=["no_forbidden_content", "language_matches"]), case("f", forbid=["poem"])) == ["instruction_following", "wrong_language"]
    assert classify(record("g", abstained=False, failed_checks=["abstention"]), case("g", answerable=False, sources=(), mention=())) == ["unsupported_answer"]
    assert classify(record("h", retrieved=["retries.md"], context=["retries.md"], invalid=[7], failed_checks=["no_fabricated_citation"]), case("h")) == ["fabricated_citation"]
    assert classify(record("i", failed_checks=["has_citation"], retrieved=["retries.md"], context=["retries.md"]), case("i")) == ["unclassified"]


def test_rollup_prioritize_and_render(tmp_path: Path) -> None:
    cases = [case("a"), case("b"), case("c", answerable=False, sources=(), mention=())]
    records = [
        record("a", abstained=True, retrieved=["fusion.md"], context=["fusion.md"], failed_checks=["abstention"]),
        record("b", retrieved=["retries.md"], context=["retries.md"], failed_checks=["language_matches"]),
        record("c", abstained=False, failed_checks=["abstention"]),
    ]
    tagged = tag_records(records, cases)
    by_type, by_stage = rollup(tagged)
    assert by_type == Counter({"retrieval_miss": 1, "wrong_language": 1, "unsupported_answer": 1})
    assert by_stage == Counter({"retrieval": 1, "generation": 2})
    ranked = prioritize(by_type)
    assert [name for name, _, _ in ranked] == ["retrieval_miss", "unsupported_answer", "wrong_language"]  # severity 3, 3, 1; ties by name
    assert ranked[0][2] == 1 * TAXONOMY["retrieval_miss"].severity  # one occurrence x severity 3
    report = render_analysis(tagged, "analysis")
    assert "## Priorities" in report and "| retrieval | 1 |" in report and "**a**" in report and "Suggested order of fixes" in report
    regressions = tmp_path / "regressions.jsonl"
    assert append_regressions(regression_cases(tagged, cases), regressions) == 3
    assert append_regressions(regression_cases(tagged, cases), regressions) == 0
    assert len(regressions.read_text(encoding="utf-8").splitlines()) == 3
