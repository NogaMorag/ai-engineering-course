"""LLM client: our error hierarchy, bounded retries, timeouts, a fallback path, and a fake for tests."""

from __future__ import annotations

import os
import random
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

from google import genai
from google.genai import types


class LLMError(Exception):
    retryable = False

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class LLMRateLimited(LLMError):
    retryable = True


class LLMUnavailable(LLMError):
    retryable = True


class LLMBadRequest(LLMError):
    pass


class LLMTruncated(LLMError):
    pass


def classify(exc: BaseException) -> LLMError:
    status = getattr(exc, "status_code", None)
    message = f"{type(exc).__name__}: {getattr(exc, 'message', None) or exc}"
    if status == 429:
        return LLMRateLimited(message, status_code=status)
    if isinstance(status, int) and status >= 500:
        return LLMUnavailable(message, status_code=status)
    if isinstance(status, int) and 400 <= status < 500:
        return LLMBadRequest(message, status_code=status)
    if isinstance(exc, TimeoutError | ConnectionError) or "Timeout" in type(exc).__name__ or "Connect" in type(exc).__name__:
        return LLMUnavailable(message)
    return LLMError(message)


@dataclass
class Completion:
    text: str
    status: str
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    attempts: int = 1
    latency_s: float = 0.0
    model: str = ""


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_delay_s: float = 1.0
    max_delay_s: float = 15.0
    total_deadline_s: float = 60.0

    def delay(self, attempt: int, rng: random.Random) -> float:
        return rng.uniform(0, min(self.max_delay_s, self.base_delay_s * (2 ** (attempt - 1))))


def with_retries(operation: Callable[[], Completion], policy: RetryPolicy, *, sleep=time.sleep, clock=time.monotonic, rng: random.Random | None = None) -> Completion:
    rng = rng or random.Random()
    started = clock()
    for attempt in range(1, policy.max_attempts + 1):
        try:
            completion = operation()
        except LLMError as err:
            if not err.retryable or attempt == policy.max_attempts:
                raise
            wait = policy.delay(attempt, rng)
            if clock() - started + wait > policy.total_deadline_s:
                raise LLMUnavailable(f"deadline of {policy.total_deadline_s}s exhausted after {attempt} attempts") from err
            sleep(wait)
            continue
        completion.attempts = attempt
        return completion
    raise AssertionError("unreachable")


class LLMClient(Protocol):
    model: str

    def complete(self, prompt: str, *, system: str | None = None, max_output_tokens: int = 1024, temperature: float = 0.2, response_format: dict[str, Any] | None = None) -> Completion: ...


class GeminiClient:
    def __init__(self, model: str | None = None, *, timeout_s: float = 60.0, policy: RetryPolicy | None = None, log: Callable[[str], None] | None = None) -> None:
        self.model = model or os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite")
        self.policy = policy or RetryPolicy()
        self.log = log or (lambda line: print(line, file=sys.stderr))
        self.client = genai.Client(http_options=types.HttpOptions(timeout=int(timeout_s * 1000), retry_options=types.HttpRetryOptions(attempts=1)))

    def complete(self, prompt: str, *, system: str | None = None, max_output_tokens: int = 1024, temperature: float = 0.2, response_format: dict[str, Any] | None = None) -> Completion:
        def operation() -> Completion:
            started = time.monotonic()
            kwargs: dict[str, Any] = {"model": self.model, "input": prompt, "generation_config": {"temperature": temperature, "max_output_tokens": max_output_tokens}}
            if system:
                kwargs["system_instruction"] = system
            if response_format:
                kwargs["response_format"] = response_format
            try:
                interaction = self.client.interactions.create(**kwargs)
            except Exception as exc:
                raise classify(exc) from exc
            usage = interaction.usage
            status = str(interaction.status or "unknown")
            if status == "incomplete":
                raise LLMTruncated(f"output cut at {max_output_tokens} tokens")
            return Completion(
                text=interaction.output_text or "", status=status, model=self.model,
                input_tokens=(usage.total_input_tokens if usage else None) or 0, output_tokens=(usage.total_output_tokens if usage else None) or 0,
                cached_tokens=(getattr(usage, "total_cached_tokens", None) if usage else None) or 0, latency_s=time.monotonic() - started,
            )

        return with_retries(operation, self.policy)


@dataclass
class FakeClient:
    """Scripted answers (str) or failures (Exception) in order. `default` answers when the script runs out."""

    script: list[str | Exception] = field(default_factory=list)
    default: str | None = None
    model: str = "fake-model"
    calls: list[dict[str, Any]] = field(default_factory=list)

    def complete(self, prompt: str, *, system: str | None = None, max_output_tokens: int = 1024, temperature: float = 0.2, response_format: dict[str, Any] | None = None) -> Completion:
        self.calls.append({"prompt": prompt, "system": system, "response_format": response_format, "max_output_tokens": max_output_tokens})
        if self.script:
            item = self.script.pop(0)
        elif self.default is not None:
            item = self.default
        else:
            raise AssertionError("FakeClient script exhausted")
        if isinstance(item, Exception):
            raise item
        return Completion(text=item, status="completed", model=self.model, input_tokens=max(1, len(prompt) // 4), output_tokens=max(1, len(item) // 4))


@dataclass
class Outcome:
    completion: Completion | None
    source: str  # primary | fallback | degraded
    errors: list[str] = field(default_factory=list)


def resilient_complete(primary: LLMClient, prompt: str, *, fallback: LLMClient | None = None, **kwargs: Any) -> Outcome:
    """Primary (with its own retries), then the fallback, then a degraded outcome. Every path is recorded."""
    errors: list[str] = []
    for client, source in ((primary, "primary"), (fallback, "fallback")):
        if client is None:
            continue
        try:
            return Outcome(client.complete(prompt, **kwargs), source, errors)
        except LLMError as err:
            errors.append(f"{source}: {err}")
    return Outcome(None, "degraded", errors)
