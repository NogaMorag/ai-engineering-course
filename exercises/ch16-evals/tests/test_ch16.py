"""Offline tests for chapter 16. Copy to ai-course/tests/test_ch16.py and run: uv run pytest -q"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ch11.llm_client import FakeClient
from ch12.embedder import FakeEmbedder
from ch15.cli import run
from ch16.cases import Case, Expectation, load_cases, validate_cases
from ch16.checks import is_hebrew, passed_all, run_checks
from ch16.harness import evaluate_case, read_records, run_cases, write_records
from ch16.judge import FaithfulnessJudge, agreement, cohens_kappa, position_bias_probe
from ch16.report import compare, render_markdown, summarize

SAMPLE_NOTES = Path(__file__).resolve().parent.parent / "ch15" / "data" / "sample-notes"


def make_case(cid: str, question: str, *, answerable: bool = True, mention=(), forbid=(), sources=(), split: str = "dev", group: str | None = None, category: str = "direct") -> Case:
    return Case(id=cid, question=question, category=category, group=group or cid, split=split,
                expected=Expectation(answerable=answerable, must_mention_any=list(mention), must_not_mention=list(forbid), source_paths=list(sources), reference="ref"))


def grounded(answer: str, citations: list[int], supported: bool = True) -> str:
    return json.dumps({"answer": answer, "citations": citations, "supported": supported})


def test_cases_file_is_sound() -> None:
    cases = load_cases()
    assert len(cases) == 30 and validate_cases(cases) == []
    assert len(load_cases(split="dev")) == 20 and len(load_cases(split="holdout")) == 10
    assert {c.category for c in cases} == {"direct", "paraphrase", "multi-hop", "unanswerable", "adversarial", "hebrew"}


def test_validate_cases_catches_leakage_duplicates_and_empty_expectations() -> None:
    leak = [make_case("a", "q1", group="g", split="dev", mention=["x"]), make_case("b", "q1 reworded", group="g", split="holdout", mention=["x"], category="paraphrase")]
    problems = validate_cases(leak)
    assert any("straddles" in p for p in problems)
    dup = [make_case("a", "q", mention=["x"]), make_case("a", "q2", mention=["x"])]
    assert any("duplicate id" in p for p in validate_cases(dup))
    empty = [make_case("c", "q")]
    assert any("nothing to check" in p for p in validate_cases(empty))
    wrong = [make_case("d", "q", answerable=False, mention=["x"], category="unanswerable")]
    assert any("cannot require" in p for p in validate_cases(wrong))


def test_deterministic_checks() -> None:
    case = make_case("c", "אילו שגיאות לא מנסים שוב?", mention=["400", "401"], forbid=["שיר"], sources=["retries.md"])
    good = run_checks(case, answer="400 ו־401 לא מנסים שוב [1].", abstained=False, citations=[1], invalid_citations=[], cited_paths=["notes/retries.md"])
    assert passed_all(good) and {c.name for c in good} == {"abstention", "no_fabricated_citation", "has_citation", "mentions_key_fact", "no_forbidden_content", "cites_expected_source", "language_matches"}
    english = run_checks(case, answer="Do not retry 400 or 401 errors [1].", abstained=False, citations=[1], invalid_citations=[], cited_paths=["retries.md"])
    assert [c.name for c in english if not c.passed] == ["language_matches"]
    abstained = run_checks(case, answer="לא מצאתי", abstained=True, citations=[], invalid_citations=[], cited_paths=[])
    assert [c.name for c in abstained if not c.passed] == ["abstention"] and len(abstained) == 2
    fabricated = run_checks(case, answer="400 [7]", abstained=False, citations=[], invalid_citations=[7], cited_paths=[])
    assert {c.name for c in fabricated if not c.passed} == {"no_fabricated_citation", "has_citation", "cites_expected_source"}
    unanswerable = make_case("u", "capital of Australia?", answerable=False, category="unanswerable")
    assert passed_all(run_checks(unanswerable, answer="", abstained=True, citations=[], invalid_citations=[], cited_paths=[]))
    assert is_hebrew("שלום עולם world") and not is_hebrew("hello עולם world")


def test_judge_parsing_agreement_and_kappa() -> None:
    fake = FakeClient(script=[json.dumps({"faithful": True, "correctness": 2, "reasoning": "matches"})])
    verdict = FaithfulnessJudge(fake).judge("q", "[1] source", "answer", "reference")
    assert verdict.faithful and verdict.correctness == 2 and "<reference_answer>" in fake.calls[0]["prompt"]
    assert agreement([True, True, False, True], [True, False, False, True]) == 0.75
    assert cohens_kappa([True, True, False, False], [True, True, False, False]) == 1.0
    assert abs(cohens_kappa([True, True, False, False], [True, False, True, False])) < 1e-9  # chance level
    assert cohens_kappa(["a"] * 4, ["a"] * 4) == 1.0
    with pytest.raises(ValueError):
        cohens_kappa([True], [True, False])


def test_position_bias_probe() -> None:
    always_slot_a = position_bias_probe(lambda a, b: "A", "short answer", "a much longer answer with detail")
    assert not always_slot_a["consistent"] and always_slot_a == {"first": "answer_a", "second": "answer_b", "consistent": False}
    prefers_longer = position_bias_probe(lambda a, b: "A" if len(a) > len(b) else "B", "short", "much longer answer")
    assert prefers_longer["consistent"] and prefers_longer["first"] == "answer_b"


@pytest.fixture
def answer_fn_factory(tmp_path: Path):
    def factory(script: list[str]):
        client = FakeClient(script=script)

        def answer_fn(question: str):
            return run(question, SAMPLE_NOTES, client=client, embedder=FakeEmbedder(), store_dir=tmp_path, mode="hybrid", k=3)

        return answer_fn

    return factory


def test_harness_records_write_read_report_and_compare(answer_fn_factory, tmp_path: Path) -> None:
    cases = [
        make_case("r1", "which failures are safe to retry?", mention=["transient", "429"], sources=["retries.md"]),
        make_case("u1", "who won the 1998 world cup?", answerable=False, category="unanswerable"),
    ]
    good = answer_fn_factory([grounded("Only transient failures such as 429 and 5xx. [1]", [1]), grounded("", [], supported=False)])
    records = run_cases(cases, good)
    assert [r.passed for r in records] == [True, True] and records[0].cited_paths == ["retries.md"] and "retries.md" in records[0].retrieved_paths
    path = tmp_path / "run.jsonl"
    write_records(records, path)
    loaded = read_records(path)
    assert loaded[0]["case_id"] == "r1" and summarize(loaded)["ALL"]["passed"] == 2
    report = render_markdown(loaded, "run A")
    assert "| ALL | 2/2 |" in report and "Failing cases" not in report

    bad = answer_fn_factory([grounded("Retry everything.", [1]), grounded("France won in 1998.", [1])])
    worse = [r.as_dict() for r in run_cases(cases, bad)]
    assert [r["passed"] for r in worse] == [False, False]
    diff = compare(loaded, worse, "A", "B")
    assert "Broken by B: r1, u1" in diff and "Fixed by B: none" in diff


def test_repeats_detect_flaky_cases(answer_fn_factory) -> None:
    case = make_case("f1", "which failures are safe to retry?", mention=["transient"], sources=["retries.md"])
    flaky = answer_fn_factory([grounded("No idea.", [1]), grounded("Transient ones. [1]", [1]), grounded("Transient ones. [1]", [1])])
    record = evaluate_case(case, flaky, repeats=3)
    assert record.runs == 3 and record.passes == 2 and record.flaky and record.passed
    with_judge = answer_fn_factory([grounded("Transient failures only. [1]", [1]), json.dumps({"faithful": True, "correctness": 2, "reasoning": "ok"})])
    judged = evaluate_case(case, with_judge, judge=FaithfulnessJudge(with_judge.__closure__[0].cell_contents))
    assert judged.judge == {"faithful": True, "correctness": 2, "reasoning": "ok"}
