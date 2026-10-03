"""Chapter 18 starter: the conftest.py for the learner's ai-course/tests folder.

Tiers:
    default          offline: fakes, cassettes, snapshots, properties. Runs on every push, < 10 s.
    -m judge         LLM-as-judge evals. Nightly. Needs a key.
    --live           live smoke tests against the real API. Weekly, or on demand. Needs a key.
"""

from __future__ import annotations

import os

import pytest


def live_enabled(flag: bool, key_present: bool) -> tuple[bool, str]:
    """Pure decision so it can be unit tested: (run?, reason when skipped)."""
    if not flag:
        return False, "live tests run only with --live"
    if not key_present:
        return False, "GEMINI_API_KEY (or GOOGLE_API_KEY) is not set"
    return True, ""


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--live", action="store_true", default=False, help="run tests marked live against the real API")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "live: calls the real API; needs a key and --live")
    config.addinivalue_line("markers", "judge: LLM-as-judge evals; slow and paid; run nightly")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    key_present = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    run_live, reason = live_enabled(config.getoption("--live"), key_present)
    if run_live:
        return
    skip_live = pytest.mark.skip(reason=reason)
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


class TokenBudget:
    """Fail a test that spends more than it should. Tests call budget.charge(completion)."""

    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.spent = 0

    def charge(self, completion) -> None:
        self.spent += completion.input_tokens + completion.output_tokens
        if self.spent > self.limit:
            pytest.fail(f"token budget exceeded: {self.spent} > {self.limit}")


@pytest.fixture
def token_budget() -> TokenBudget:
    return TokenBudget(limit=int(os.environ.get("AI_COURSE_TEST_TOKEN_BUDGET", "4000")))
