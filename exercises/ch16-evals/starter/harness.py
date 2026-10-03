"""Chapter 16 starter: run the cases against a system under test, record everything, grade with code and (optionally) a judge."""

from __future__ import annotations

import json
import math
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ch15.answer import Answer, build_context
from ch15.cli import Trace
from ch16.cases import Case
from ch16.checks import passed_all, run_checks
from ch16.judge import FaithfulnessJudge

AnswerFn = Callable[[str], tuple[Answer, Trace]]


@dataclass
class EvalRecord:
    case_id: str
    category: str
    split: str
    question: str
    answer: str
    abstained: bool
    supported: bool
    citations: list[int]
    invalid_citations: list[int]
    retrieved_paths: list[str]
    context_paths: list[str]
    cited_paths: list[str]
    sources_text: str
    checks: list[dict[str, Any]]
    passed: bool
    runs: int = 1
    passes: int = 1
    flaky: bool = False
    judge: dict[str, Any] | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_once(case: Case, answer_fn: AnswerFn) -> EvalRecord:
    started = time.monotonic()
    answer, trace = answer_fn(case.question)
    cited_paths = [answer.sources[n - 1].chunk.path for n in answer.citations if 0 < n <= len(answer.sources)]
    sources_text, _ = build_context(answer.sources, max_chars=10**9)
    checks = run_checks(
        case, answer=answer.text, abstained=answer.abstained, citations=answer.citations,
        invalid_citations=answer.invalid_citations, cited_paths=cited_paths,
    )
    return EvalRecord(
        case_id=case.id, category=case.category, split=case.split, question=case.question,
        answer=answer.text, abstained=answer.abstained, supported=answer.supported,
        citations=answer.citations, invalid_citations=answer.invalid_citations,
        retrieved_paths=[r["path"] for r in trace.retrieved], context_paths=[s.chunk.path for s in answer.sources],
        cited_paths=cited_paths, sources_text=sources_text,
        checks=[asdict(c) for c in checks], passed=passed_all(checks),
        input_tokens=trace.input_tokens, output_tokens=trace.output_tokens, latency_s=round(time.monotonic() - started, 2),
    )


def evaluate_case(case: Case, answer_fn: AnswerFn, *, repeats: int = 1, judge: FaithfulnessJudge | None = None) -> EvalRecord:
    """Run once; if it fails and repeats > 1, run again to tell flaky from broken. Majority decides."""
    record = evaluate_once(case, answer_fn)
    if not record.passed and repeats > 1:
        outcomes = [record] + [evaluate_once(case, answer_fn) for _ in range(repeats - 1)]
        passes = sum(1 for r in outcomes if r.passed)
        record = outcomes[0]
        record.runs, record.passes = len(outcomes), passes
        record.flaky = 0 < passes < len(outcomes)
        record.passed = passes >= math.ceil(len(outcomes) / 2)
        record.input_tokens = sum(r.input_tokens for r in outcomes)
        record.output_tokens = sum(r.output_tokens for r in outcomes)
    if judge and case.expected.answerable and not record.abstained:
        verdict = judge.judge(case.question, record.sources_text, record.answer, case.expected.reference)
        record.judge = verdict.model_dump()
    return record


def run_cases(cases: list[Case], answer_fn: AnswerFn, *, repeats: int = 1, judge: FaithfulnessJudge | None = None, on_record: Callable[[EvalRecord], None] | None = None) -> list[EvalRecord]:
    records = []
    for case in cases:
        record = evaluate_case(case, answer_fn, repeats=repeats, judge=judge)
        records.append(record)
        if on_record:
            on_record(record)
    return records


def write_records(records: list[EvalRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r.as_dict(), ensure_ascii=False) + "\n" for r in records), encoding="utf-8")


def read_records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
