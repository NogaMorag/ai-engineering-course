"""Offline tests for chapter 23. Copy to ai-course/tests/test_ch23.py and run: uv run pytest -q"""

from __future__ import annotations

import pytest

from ch11.llm_client import (
    Completion,
    FakeClient,
    LLMBadRequest,
    LLMRateLimited,
    LLMUnavailable,
    RetryPolicy,
)
from ch22.tracing import PRICES, estimate_cost
from ch23.bench import BenchResult, percentile, render_table
from ch23.budget import BudgetExceeded, BudgetGuard
from ch23.resilient import CircuitBreaker, degraded_summary, resilient_call


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


def test_percentiles_and_table() -> None:
    values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    assert percentile(values, 50) == 5.0 and percentile(values, 95) == 10.0 and percentile([3.0], 95) == 3.0
    with pytest.raises(ValueError):
        percentile([], 50)
    result = BenchResult("gemini-3.5-flash-lite", 10, values, [0.4, 0.5, 0.6], 10_000, 2_000)
    row = result.row()
    assert row["p50_s"] == 5.0 and row["p95_s"] == 10.0 and row["ttft_p50_s"] == 0.5
    assert row["cost_per_call_usd"] == round(estimate_cost("gemini-3.5-flash-lite", 1000, 200), 6)
    table = render_table([row])
    assert table.startswith("| model |") and "gemini-3.5-flash-lite" in table


def test_estimate_cost_uses_the_price_table_and_cached_discount() -> None:
    price_in, price_out = PRICES["gemini-3.5-flash-lite"][:2]
    assert estimate_cost("gemini-3.5-flash-lite", 1_000_000, 0) == pytest.approx(price_in)
    assert estimate_cost("gemini-3.5-flash-lite", 0, 1_000_000) == pytest.approx(price_out)
    full = estimate_cost("gemini-3.5-flash-lite", 1_000_000, 0)
    with_cache = estimate_cost("gemini-3.5-flash-lite", 0, 0, cached_tokens=1_000_000)
    assert 0 < with_cache < full
    assert estimate_cost("unknown-model", 1000, 1000) == 0.0  # unknown price is reported as 0 and flagged in the report, never invented


def test_budget_guard_stops_the_run() -> None:
    guard = BudgetGuard(max_usd=0.001)
    cheap = Completion(text="x", status="completed", input_tokens=100, output_tokens=10)
    guard.charge("gemini-3.5-flash-lite", cheap)
    assert guard.calls == 1 and guard.remaining_usd < 0.001
    huge = Completion(text="x", status="completed", input_tokens=5_000_000, output_tokens=1_000_000)
    with pytest.raises(BudgetExceeded, match="budget"):
        guard.charge("gemini-3.5-flash-lite", huge)
    assert guard.by_model["gemini-3.5-flash-lite"] == pytest.approx(guard.spent_usd)


def test_circuit_breaker_states() -> None:
    clock = Clock()
    breaker = CircuitBreaker(failure_threshold=2, cooldown_s=10, clock=clock)
    assert breaker.allow()
    breaker.record_failure()
    assert breaker.state == "closed" and breaker.allow()
    breaker.record_failure()
    assert breaker.state == "open" and not breaker.allow()
    clock.now = 10.0
    assert breaker.allow() and breaker.state == "half-open"
    breaker.record_failure()
    assert breaker.state == "open" and breaker.opened_at == 10.0
    clock.now = 25.0
    assert breaker.allow()
    breaker.record_success()
    assert breaker.state == "closed" and breaker.failures == 0


def test_resilient_call_primary_then_fallback_then_degraded() -> None:
    clock = Clock()
    policy = RetryPolicy(max_attempts=2, base_delay_s=0.0, max_delay_s=0.0, total_deadline_s=30)
    ok = resilient_call(FakeClient(script=["fine"]), "p", fallback=FakeClient(script=["fb"]), policy=policy, clock=clock, sleep=clock.sleep)
    assert ok.source == "primary" and ok.text == "fine" and ok.attempts == 1 and ok.errors == []

    flaky = FakeClient(script=[LLMRateLimited("429"), "recovered"])
    retried = resilient_call(flaky, "p", policy=policy, clock=clock, sleep=clock.sleep)
    assert retried.source == "primary" and retried.text == "recovered" and retried.attempts == 2

    down = FakeClient(script=[LLMUnavailable("503"), LLMUnavailable("503")])
    fell = resilient_call(down, "p", fallback=FakeClient(script=["from fallback"]), policy=policy, clock=clock, sleep=clock.sleep)
    assert fell.source == "fallback" and fell.text == "from fallback" and any("503" in e for e in fell.errors)

    bad = FakeClient(script=[LLMBadRequest("400")])
    degraded = resilient_call(bad, "p", fallback=FakeClient(script=[LLMBadRequest("400")]), degrade=degraded_summary, policy=policy, clock=clock, sleep=clock.sleep)
    assert degraded.source == "degraded" and degraded.completion is not None and degraded.completion.status == "degraded"
    assert len(degraded.errors) == 2 and all("LLMBadRequest" in e for e in degraded.errors)

    nothing = resilient_call(bad.__class__(script=[LLMBadRequest("400")]), "p", policy=policy, clock=clock, sleep=clock.sleep)
    assert nothing.source == "degraded" and nothing.completion is None


def test_resilient_call_respects_deadline_and_open_breaker() -> None:
    clock = Clock()
    policy = RetryPolicy(max_attempts=5, base_delay_s=10.0, max_delay_s=10.0, total_deadline_s=100)
    slow = FakeClient(script=[LLMUnavailable("timeout")] * 5)
    out = resilient_call(slow, "p", fallback=FakeClient(script=["fb"]), deadline_s=12, policy=policy, clock=clock, sleep=clock.sleep)
    assert out.source == "fallback" and clock.now <= 12.0 + 1e-9

    clock = Clock()
    breaker = CircuitBreaker(failure_threshold=1, cooldown_s=60, clock=clock)
    breaker.record_failure()
    primary = FakeClient(script=["never called"])
    out = resilient_call(primary, "p", fallback=FakeClient(script=["fb"]), breaker=breaker, policy=policy, clock=clock, sleep=clock.sleep)
    assert out.source == "fallback" and primary.calls == [] and any("circuit open" in e for e in out.errors)
