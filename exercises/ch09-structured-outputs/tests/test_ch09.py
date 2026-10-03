"""Offline tests for chapter 9. Copy to ai-course/tests/test_ch09.py and run: uv run pytest -q"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from ch09.schemas import RESPONSE_FORMAT, ArticleSummary, clean_schema
from ch09.summarize_structured import OutputTruncated, SummaryError, summarize

VALID = {
    "is_article": True,
    "headline": "Cargo-Lite 2.0 adds a shared build cache",
    "bullets": ["Version 2.0 was released.", "Builds dropped from 41 to 6 minutes.", "The old config format goes away in 3.0."],
    "why_it_matters": "Why it matters: faster builds for Rust teams.",
    "tags": ["rust", "build tools"],
    "confidence": "high",
}


class FakeBackend:
    def __init__(self, scripted: list[tuple[str, str]]) -> None:
        self.scripted = list(scripted)
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> tuple[str, str]:
        self.prompts.append(prompt)
        return self.scripted.pop(0)


def test_schema_has_no_titles_or_refs_and_keeps_descriptions() -> None:
    schema = RESPONSE_FORMAT["schema"]
    dumped = json.dumps(schema)
    assert '"title"' not in dumped and "$defs" not in dumped and "$ref" not in dumped
    assert "description" in schema["properties"]["bullets"]
    assert set(schema["required"]) == {"is_article", "headline", "bullets", "why_it_matters", "tags", "confidence"}
    assert clean_schema({"title": "x", "a": [{"title": "y", "b": 1}]}) == {"a": [{"b": 1}]}


def test_valid_article_and_valid_non_article() -> None:
    assert ArticleSummary.model_validate(VALID).confidence == "high"
    non_article = {"is_article": False, "headline": "", "bullets": [], "why_it_matters": "", "tags": [], "confidence": "low"}
    assert ArticleSummary.model_validate(non_article).is_article is False


def test_rules_the_schema_cannot_express() -> None:
    with pytest.raises(ValidationError):
        ArticleSummary.model_validate({**VALID, "bullets": VALID["bullets"][:2]})
    with pytest.raises(ValidationError):
        ArticleSummary.model_validate({**VALID, "why_it_matters": "It matters."})
    with pytest.raises(ValidationError):
        ArticleSummary.model_validate({**VALID, "headline": " ".join(["word"] * 13)})


def test_summarize_returns_on_first_valid_output() -> None:
    backend = FakeBackend([(json.dumps(VALID), "completed")])
    summary = summarize(backend, "some article")
    assert summary.headline.startswith("Cargo-Lite")
    assert len(backend.prompts) == 1 and "<article>" in backend.prompts[0]


def test_summarize_repairs_once_after_invalid_json() -> None:
    backend = FakeBackend([("not json at all", "completed"), (json.dumps(VALID), "completed")])
    summary = summarize(backend, "some article")
    assert summary.is_article is True
    assert len(backend.prompts) == 2
    assert "rejected by the validator" in backend.prompts[1]


def test_summarize_repairs_once_after_rule_violation() -> None:
    four_bullets = {**VALID, "bullets": VALID["bullets"] + ["One bullet too many."]}
    backend = FakeBackend([(json.dumps(four_bullets), "completed"), (json.dumps(VALID), "completed")])
    assert summarize(backend, "some article").is_article is True
    assert "exactly three bullets" in backend.prompts[1]


def test_summarize_gives_up_after_max_attempts() -> None:
    backend = FakeBackend([("{}", "completed"), ("{}", "completed")])
    with pytest.raises(SummaryError):
        summarize(backend, "some article", max_attempts=2)


def test_truncated_output_is_not_retried() -> None:
    backend = FakeBackend([('{"is_article": true, "headline": "cut', "incomplete")])
    with pytest.raises(OutputTruncated):
        summarize(backend, "some article")
    assert len(backend.prompts) == 1
