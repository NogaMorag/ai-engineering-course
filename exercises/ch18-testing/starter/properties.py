"""Chapter 18 starter: property-style assertions for nondeterministic output.

We cannot assert the exact text a model returns. We can assert properties that EVERY acceptable
output has. Each checker returns the list of violated properties (empty = all hold).
"""

from __future__ import annotations

import json
import random
from typing import Any


def article_summary_violations(data: dict[str, Any]) -> list[str]:
    violations = []
    if data.get("is_article"):
        if len(data.get("bullets", [])) != 3:
            violations.append("exactly three bullets")
        if not str(data.get("headline", "")).strip():
            violations.append("headline present")
        if len(str(data.get("headline", "")).split()) > 12:
            violations.append("headline at most 12 words")
        if not str(data.get("why_it_matters", "")).startswith("Why it matters:"):
            violations.append("why_it_matters prefix")
        if not 1 <= len(data.get("tags", [])) <= 4:
            violations.append("one to four tags")
        if any(t != t.lower() for t in data.get("tags", [])):
            violations.append("tags lowercase")
    else:
        if data.get("headline") or data.get("bullets") or data.get("why_it_matters"):
            violations.append("non-article has empty fields")
    if data.get("confidence") not in {"high", "medium", "low"}:
        violations.append("confidence in enum")
    return violations


def grounded_answer_violations(data: dict[str, Any], n_sources: int) -> list[str]:
    violations = []
    citations = data.get("citations", [])
    if any(not isinstance(c, int) or c < 1 or c > n_sources for c in citations):
        violations.append("citations within 1..n_sources")
    if data.get("supported") and not citations:
        violations.append("supported answers cite something")
    if data.get("supported") and not str(data.get("answer", "")).strip():
        violations.append("supported answers are not empty")
    if not data.get("supported") and str(data.get("answer", "")).strip():
        violations.append("unsupported answers are empty")
    return violations


def parses_as_json(text: str) -> bool:
    try:
        json.loads(text)
    except (TypeError, ValueError):
        return False
    return True


def random_article_summary(rng: random.Random, *, valid: bool = True) -> dict[str, Any]:
    """A generator for property tests: valid summaries by default, or one with a random defect."""
    words = ["cache", "release", "cluster", "driver", "policy", "survey", "fab", "orbit", "battery", "rollout", "schema", "index"]
    data = {
        "is_article": True,
        "headline": " ".join(rng.choice(words) for _ in range(rng.randint(3, 12))),
        "bullets": [f"Fact {i} about {rng.choice(words)}." for i in range(3)],
        "why_it_matters": f"Why it matters: {rng.choice(words)} changes.",
        "tags": [rng.choice(words) for _ in range(rng.randint(1, 4))],
        "confidence": rng.choice(["high", "medium", "low"]),
    }
    if not valid:
        defect = rng.choice(["bullets", "headline", "prefix", "tags", "confidence"])
        if defect == "bullets":
            data["bullets"] = data["bullets"][:2]
        elif defect == "headline":
            data["headline"] = " ".join(["word"] * 13)
        elif defect == "prefix":
            data["why_it_matters"] = "It matters."
        elif defect == "tags":
            data["tags"] = []
        else:
            data["confidence"] = "certain"
    return data
