"""Chapter 23 starter: calls that degrade gracefully.

    deadline        the whole request, including retries and the fallback, must finish in time
    retry policy    chapter 11's with_retries, bounded by the remaining deadline
    circuit breaker stop hammering a model that keeps failing; try again after a cooldown
    fallback        a second model when the first is unavailable; recorded, never silent
    degradation     when everything fails, return a result that keeps the contract and says so
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from ch11.llm_client import Completion, LLMClient, LLMError, RetryPolicy, with_retries

Source = Literal["primary", "fallback", "degraded"]


class CircuitOpen(LLMError):
    """The breaker is open: the model failed too often recently; not even trying."""

    retryable = False


@dataclass
class CircuitBreaker:
    """closed (normal) -> open after `failure_threshold` consecutive failures -> half-open after `cooldown_s`:
    one trial call; success closes the breaker, failure opens it again."""

    failure_threshold: int = 3
    cooldown_s: float = 30.0
    clock: Callable[[], float] = time.monotonic
    failures: int = 0
    opened_at: float | None = None
    state: Literal["closed", "open", "half-open"] = "closed"

    def allow(self) -> bool:
        # TODO 1: closed -> True; open -> become half-open and return True once cooldown_s has passed since
        # opened_at, else False; half-open -> True (one trial call).
        raise NotImplementedError

    def record_success(self) -> None:
        self.failures, self.opened_at, self.state = 0, None, "closed"

    def record_failure(self) -> None:
        self.failures += 1
        if self.state == "half-open" or self.failures >= self.failure_threshold:
            self.state, self.opened_at = "open", self.clock()


@dataclass
class Outcome:
    completion: Completion | None
    source: Source
    attempts: int = 0
    errors: list[str] = field(default_factory=list)
    elapsed_s: float = 0.0

    @property
    def text(self) -> str:
        return self.completion.text if self.completion else ""


def _remaining(deadline_at: float, clock: Callable[[], float]) -> float:
    return max(0.0, deadline_at - clock())


def resilient_call(
    primary: LLMClient,
    prompt: str,
    *,
    fallback: LLMClient | None = None,
    breaker: CircuitBreaker | None = None,
    deadline_s: float = 60.0,
    policy: RetryPolicy | None = None,
    degrade: Callable[[list[str]], Completion] | None = None,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    **kwargs: Any,
) -> Outcome:
    """Primary with bounded retries, then fallback, then degradation. Every path records what happened."""
    started = clock()
    deadline_at = started + deadline_s
    policy = policy or RetryPolicy(max_attempts=3, total_deadline_s=deadline_s)
    breaker = breaker or CircuitBreaker(clock=clock)
    outcome = Outcome(completion=None, source="degraded")

    def attempt(client: LLMClient, source: Source) -> bool:
        budget = _remaining(deadline_at, clock)
        if budget <= 0:
            outcome.errors.append(f"{source}: deadline exhausted before the call")
            return False
        bounded = RetryPolicy(policy.max_attempts, policy.base_delay_s, policy.max_delay_s, min(policy.total_deadline_s, budget))
        try:
            completion = with_retries(lambda: client.complete(prompt, **kwargs), bounded, sleep=sleep, clock=clock)
        except LLMError as err:
            outcome.attempts += getattr(err, "attempts", 1)
            outcome.errors.append(f"{source}: {type(err).__name__}: {err}")
            return False
        outcome.attempts += completion.attempts
        outcome.completion, outcome.source = completion, source
        return True

    # TODO 2: if breaker.allow(): try the primary (attempt(primary, "primary")); success -> record_success and
    # return; failure -> record_failure. Else record "primary: circuit open (...)" in outcome.errors.
    # Then the fallback if given; then degrade(outcome.errors) if given. Set elapsed_s before every return.
    raise NotImplementedError


def degraded_summary(errors: list[str]) -> Completion:
    """Keeps the contract (a Completion with text) and says plainly that this is not a model answer."""
    return Completion(text="Summary unavailable right now; the source article is linked below.", status="degraded", attempts=0)
