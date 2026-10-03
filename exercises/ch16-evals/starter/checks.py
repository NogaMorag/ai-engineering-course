"""Chapter 16 starter: deterministic checks. Where code can judge, code judges; the LLM judge comes after."""

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
    # TODO 1: build the list of CheckResult: "abstention" (abstained == not answerable) and
    # "no_fabricated_citation" always; when answerable and not abstained also "has_citation",
    # "mentions_key_fact" (any must_mention_any term, case-insensitive), "no_forbidden_content",
    # "cites_expected_source" (compare file names), and "language_matches" (is_hebrew of answer vs question;
    # skip it when the answer has no letters at all).
    raise NotImplementedError


def passed_all(results: list[CheckResult]) -> bool:
    return all(r.passed for r in results)
