"""Chapter 18 solution: the conftest.py for the learner's ai-course/tests folder.

Tiers:
    default          offline: fakes, cassettes, snapshots, properties. Runs on every push, < 10 s.
    --judge          LLM-as-judge evals. Nightly. Needs a key (skipped otherwise, like live).
    --live           live smoke tests against the real API. Weekly, or on demand. Needs a key.
"""

from __future__ import annotations

import os

import pytest


def tier_enabled(name: str, flag: bool, key_present: bool) -> tuple[bool, str]:
    """Pure decision so it can be unit tested: (run?, reason when skipped). Used for the live and judge tiers."""
    if not flag:
        return False, f"{name} tests run only with --{name}"
    if not key_present:
        return False, "GEMINI_API_KEY (or GOOGLE_API_KEY) is not set"
    return True, ""


def live_enabled(flag: bool, key_present: bool) -> tuple[bool, str]:
    return tier_enabled("live", flag, key_present)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--live", action="store_true", default=False, help="run tests marked live against the real API")
    parser.addoption("--judge", action="store_true", default=False, help="run tests marked judge (LLM-as-judge evals; paid)")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "live: calls the real API; needs a key and --live")
    config.addinivalue_line("markers", "judge: LLM-as-judge evals; slow and paid; needs a key and --judge")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Both paid tiers skip themselves (with a reason, visible with -rs) unless their flag and a key are present."""
    key_present = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    for name in ("live", "judge"):
        run, reason = tier_enabled(name, config.getoption(f"--{name}"), key_present)
        if run:
            continue
        marker = pytest.mark.skip(reason=reason)
        for item in items:
            if name in item.keywords:
                item.add_marker(marker)


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
