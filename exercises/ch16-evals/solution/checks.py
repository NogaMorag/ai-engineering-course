"""Chapter 16 solution: deterministic checks. Where code can judge, code judges; the LLM judge comes after."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ch16.cases import Case

HEBREW = re.compile(r"[֐-׿]")


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


def is_hebrew(text: str) -> bool:
    letters = [ch for ch in text if ch.isalpha()]
    return bool(letters) and sum(1 for ch in letters if HEBREW.match(ch)) / len(letters) > 0.5


def run_checks(case: Case, *, answer: str, abstained: bool, citations: list[int], invalid_citations: list[int], cited_paths: list[str]) -> list[CheckResult]:
    expected = case.expected
    results = [CheckResult("abstention", abstained == (not expected.answerable), f"abstained={abstained}, answerable={expected.answerable}")]
    results.append(CheckResult("no_fabricated_citation", not invalid_citations, f"invalid={invalid_citations}"))
    if expected.answerable and not abstained:
        results.append(CheckResult("has_citation", bool(citations), f"citations={citations}"))
        lowered = answer.lower()
        if expected.must_mention_any:
            hit = [t for t in expected.must_mention_any if t.lower() in lowered]
            results.append(CheckResult("mentions_key_fact", bool(hit), f"matched={hit}"))
        if expected.must_not_mention:
            leaked = [t for t in expected.must_not_mention if t.lower() in lowered]
            results.append(CheckResult("no_forbidden_content", not leaked, f"leaked={leaked}"))
        if expected.source_paths:
            cited = sorted({p.split("/")[-1] for p in cited_paths})
            ok = any(p.split("/")[-1] in cited for p in expected.source_paths)
            results.append(CheckResult("cites_expected_source", ok, f"cited={cited}"))
        if any(ch.isalpha() for ch in answer):  # an answer with no letters has no language to check
            results.append(CheckResult("language_matches", is_hebrew(answer) == is_hebrew(case.question), f"answer_hebrew={is_hebrew(answer)}"))
    return results


def passed_all(results: list[CheckResult]) -> bool:
    return all(r.passed for r in results)
