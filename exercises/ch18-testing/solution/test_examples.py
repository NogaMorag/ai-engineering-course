"""Chapter 18 solution: example tests for each tier. Copy into ai-course/tests/ as test_ch18_examples.py.

The fast tier needs no key. The cassette for the recorded test is created the first time you run with
AI_COURSE_RECORD=1 and committed; afterwards the test replays it offline.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from ch09.schemas import RESPONSE_FORMAT as SUMMARY_FORMAT
from ch09.schemas import ArticleSummary
from ch10.tools import tool_declarations
from ch11.llm_client import FakeClient
from ch11.summarize_url import summarize_text
from ch18.contracts import assert_matches_snapshot
from ch18.properties import article_summary_violations, random_article_summary
from ch18.recorder import client_for_tests

TESTS_DIR = Path(__file__).parent
ARTICLE = "Cargo-Lite 2.0 was released on Tuesday with a shared build cache. Builds at one company dropped from 41 to 6 minutes. The old configuration format is removed in 3.0."


# --- tier 1: fakes (unit tests of our own logic) -----------------------------------------------
def test_summarizer_logic_with_a_fake() -> None:
    valid = random_article_summary(random.Random(1))
    fake = FakeClient(script=[json.dumps(valid)])
    assert summarize_text(fake, ARTICLE).is_article is True
    assert fake.calls[0]["response_format"] == SUMMARY_FORMAT


# --- tier 1: contracts (what the model sees must not drift by accident) --------------------------
def test_schema_and_tool_contracts() -> None:
    snapshots = TESTS_DIR / "snapshots"
    assert_matches_snapshot("article_summary_schema", SUMMARY_FORMAT["schema"], snapshots)
    assert_matches_snapshot("tool_declarations", tool_declarations(), snapshots)


# --- tier 1: properties (hold for every acceptable output) ---------------------------------------
@pytest.mark.parametrize("seed", range(25))
def test_valid_summaries_pass_the_validator_and_invalid_ones_do_not(seed: int) -> None:
    rng = random.Random(seed)
    good = random_article_summary(rng, valid=True)
    assert article_summary_violations(good) == []
    ArticleSummary.model_validate(good)
    bad = random_article_summary(rng, valid=False)
    assert article_summary_violations(bad) != []


# --- tier 1: recorded fixture (real model output, replayed offline) -------------------------------
def test_recorded_summary_is_valid_and_grounded() -> None:
    client = client_for_tests(TESTS_DIR / "cassettes" / "summarize_cargo_lite.jsonl")
    try:
        summary = summarize_text(client, ARTICLE)
    except Exception as exc:  # a missing cassette is a setup problem, not a test failure; anything else re-raises
        if type(exc).__name__ == "CassetteMiss":
            pytest.skip(str(exc))
        raise
    assert summary.is_article and len(summary.bullets) == 3
    assert any("6" in b or "six" in b.lower() for b in summary.bullets)


# --- tier 3: live smoke (skipped unless --live and a key) ---------------------------------------
@pytest.mark.live
def test_live_model_still_returns_schema_valid_json(token_budget) -> None:
    from ch11.llm_client import GeminiClient

    client = GeminiClient()
    completion = client.complete(f"<article>\n{ARTICLE}\n</article>", system="Summarize into the schema.", max_output_tokens=400, response_format=SUMMARY_FORMAT)
    token_budget.charge(completion)
    ArticleSummary.model_validate_json(completion.text)
