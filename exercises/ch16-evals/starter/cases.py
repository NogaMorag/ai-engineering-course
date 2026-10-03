"""Chapter 16 starter: the eval cases file. Expectations are written before any answer is looked at."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["direct", "paraphrase", "multi-hop", "unanswerable", "adversarial", "hebrew"]
Split = Literal["dev", "holdout"]
CASES_PATH = Path(__file__).parent / "data" / "cases.jsonl"


class Expectation(BaseModel):
    answerable: bool
    must_mention_any: list[str] = Field(default_factory=list, description="at least one must appear in the answer")
    must_not_mention: list[str] = Field(default_factory=list)
    source_paths: list[str] = Field(default_factory=list, description="at least one must be cited when answerable")
    reference: str = ""


class Case(BaseModel):
    id: str
    question: str
    category: Category
    group: str  # paraphrases of one question share a group, and a group never straddles dev/holdout
    split: Split
    expected: Expectation


def load_cases(path: Path = CASES_PATH, split: str = "all") -> list[Case]:
    cases = [Case.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return cases if split == "all" else [c for c in cases if c.split == split]


def validate_cases(cases: list[Case]) -> list[str]:
    """Problems a cases file can have. Empty list means the file is sound."""
    problems: list[str] = []
    ids = Counter(c.id for c in cases)
    problems += [f"duplicate id {i}" for i, n in ids.items() if n > 1]
    splits_by_group: dict[str, set[str]] = {}
    for c in cases:
        splits_by_group.setdefault(c.group, set()).add(c.split)
    problems += [f"group {g} straddles dev and holdout (leakage)" for g, s in splits_by_group.items() if len(s) > 1]
    for c in cases:
        if c.expected.answerable and not c.expected.must_mention_any and not c.expected.source_paths:
            problems.append(f"{c.id}: answerable but nothing to check")
        if not c.expected.answerable and (c.expected.must_mention_any or c.expected.source_paths):
            problems.append(f"{c.id}: unanswerable cases cannot require mentions or sources")
    categories = {c.category for c in cases}
    missing = set(Category.__args__) - categories  # type: ignore[attr-defined]
    problems += [f"no cases in category {m}" for m in sorted(missing)]
    return problems
