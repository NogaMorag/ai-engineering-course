"""Chapter 11 starter: one client interface for the rest of the course. Fill in the three TODOs.

Copy to ai-course/ch11/llm_client.py (with an empty ch11/__init__.py). Run the demo from the course root:

    uv run --env-file .env python -m ch11.llm_client
"""

from __future__ import annotations

import os
import random
import sys
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any, Protocol

from google import genai
from google.genai import types

# ---------------------------------------------------------------- errors we own


class LLMError(Exception):
    """Base class for every failure the client reports."""

    retryable = False

    def __init__(self, message: str, *, status_code: int | None = None, cause: BaseException | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.__cause__ = cause


class LLMRateLimited(LLMError):
    retryable = True


class LLMUnavailable(LLMError):
    """5xx, connection problems and timeouts: the service is not answering right now."""

    retryable = True


class LLMBadRequest(LLMError):
    """4xx other than 429: our request is wrong; retrying the same request cannot help."""


class LLMTruncated(LLMError):
    """The model stopped at max_output_tokens; the output is cut."""


def classify(exc: BaseException) -> LLMError:
    """Map an SDK exception to our hierarchy using duck typing on `status_code`."""
    # TODO 1: read getattr(exc, "status_code", None). 429 -> LLMRateLimited; >= 500 -> LLMUnavailable;
    # other 4xx -> LLMBadRequest; TimeoutError/ConnectionError (or a class name containing "Timeout"
    # or "Connection") -> LLMUnavailable; anything else -> LLMError. Pass status_code= and cause=.
    raise NotImplementedError


# ---------------------------------------------------------------- the interface


@dataclass
class Completion:
    text: str
    status: str
    input_tokens: int = 0
    output_tokens: int = 0
    attempts: int = 1
    latency_s: float = 0.0


@dataclass
class RetryPolicy:
    max_attempts: int = 4
    base_delay_s: float = 1.0
    max_delay_s: float = 20.0
    total_deadline_s: float = 90.0

    def delay(self, attempt: int, rng: random.Random) -> float:
        """Full jitter: a random wait between 0 and the exponential cap. Attempt counts from 1."""
        cap = min(self.max_delay_s, self.base_delay_s * (2 ** (attempt - 1)))
        return rng.uniform(0, cap)


class LLMClient(Protocol):
    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_output_tokens: int = 1024,
        temperature: float = 0.2,
        response_format: dict[str, Any] | None = None,
    ) -> Completion: ...

    def stream(self, prompt: str, *, system: str | None = None, max_output_tokens: int = 1024) -> Iterator[str]: ...


# ---------------------------------------------------------------- the retry engine (pure, testable)


def with_retries(
    operation: Callable[[], Completion],
    policy: RetryPolicy,
    *,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
    rng: random.Random | None = None,
    on_retry: Callable[[int, LLMError, float], None] | None = None,
) -> Completion:
    """Run `operation`; retry only retryable errors, with jittered backoff and a total deadline."""
    # TODO 2: for attempt in 1..max_attempts: call operation(); on LLMError re-raise if not retryable
    # or this was the last attempt; otherwise compute wait = policy.delay(attempt, rng); if the elapsed
    # time plus wait passes total_deadline_s raise LLMUnavailable("deadline ...") from the error;
    # call on_retry if given; sleep(wait). On success set completion.attempts = attempt and return it.
    raise NotImplementedError


# ---------------------------------------------------------------- the real client


class GeminiClient:
    def __init__(
        self,
        model: str | None = None,
        *,
        timeout_s: float = 60.0,
        policy: RetryPolicy | None = None,
        log: Callable[[str], None] | None = None,
    ) -> None:
        self.model = model or os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite")
        self.policy = policy or RetryPolicy()
        self.log = log or (lambda line: print(line, file=sys.stderr))
        # SDK-level retries off (attempts=1): we own the retry policy in with_retries.
        http_options = types.HttpOptions(timeout=int(timeout_s * 1000), retry_options=types.HttpRetryOptions(attempts=1))
        self.client = genai.Client(http_options=http_options)

    def _create(self, **kwargs: Any) -> Any:
        try:
            return self.client.interactions.create(model=self.model, **kwargs)
        except Exception as exc:  # the SDK errors have no public base class we can import, so classify by status_code
            raise classify(exc) from exc

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_output_tokens: int = 1024,
        temperature: float = 0.2,
        response_format: dict[str, Any] | None = None,
    ) -> Completion:
        def operation() -> Completion:
            # TODO 3: build kwargs (input, generation_config with temperature and max_output_tokens,
            # optional system_instruction and response_format); call self._create(**kwargs); build a
            # Completion from output_text, status, usage (fields may be None) and the elapsed time;
            # if status == "incomplete" raise LLMTruncated; return the Completion.
            raise NotImplementedError

        def on_retry(attempt: int, err: LLMError, wait: float) -> None:
            self.log(f"[llm] attempt {attempt} failed ({type(err).__name__}); retrying in {wait:.1f}s")

        return with_retries(operation, self.policy, on_retry=on_retry)

    def stream(self, prompt: str, *, system: str | None = None, max_output_tokens: int = 1024) -> Iterator[str]:
        """Yield text deltas as they arrive. Not retried: a half-delivered stream cannot be replayed safely."""
        kwargs: dict[str, Any] = {
            "input": prompt,
            "stream": True,
            "generation_config": {"max_output_tokens": max_output_tokens},
        }
        if system:
            kwargs["system_instruction"] = system
        try:
            for event in self.client.interactions.create(model=self.model, **kwargs):
                if event.type == "step.delta" and getattr(event.delta, "type", None) == "text":
                    yield event.delta.text
                elif event.type == "error":
                    raise LLMError(f"stream error: {getattr(event, 'error', event)}")
        except LLMError:
            raise
        except Exception as exc:  # same reason as in _create
            raise classify(exc) from exc


# ---------------------------------------------------------------- the fake for tests


@dataclass
class FakeClient:
    """Scripted answers. An item may be a str (returned) or an Exception (raised)."""

    script: list[str | Exception] = field(default_factory=list)
    calls: list[dict[str, Any]] = field(default_factory=list)

    def _next(self) -> str:
        if not self.script:
            raise AssertionError("FakeClient script exhausted")
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_output_tokens: int = 1024,
        temperature: float = 0.2,
        response_format: dict[str, Any] | None = None,
    ) -> Completion:
        self.calls.append({"prompt": prompt, "system": system, "response_format": response_format})
        text = self._next()
        return Completion(text=text, status="completed", input_tokens=len(prompt) // 4, output_tokens=len(text) // 4)

    def stream(self, prompt: str, *, system: str | None = None, max_output_tokens: int = 1024) -> Iterator[str]:
        self.calls.append({"prompt": prompt, "system": system, "response_format": None})
        text = self._next()
        for i in range(0, len(text), 5):
            yield text[i : i + 5]


# ---------------------------------------------------------------- demo


def main() -> None:
    client = GeminiClient()
    print(f"model: {client.model}\n")

    print("--- complete ---")
    result = client.complete("In one sentence, why do production clients retry only some errors?", max_output_tokens=120)
    print(result.text)
    print(f"[status={result.status} attempts={result.attempts} tokens in/out={result.input_tokens}/{result.output_tokens} {result.latency_s:.2f}s]\n")

    print("--- stream ---")
    started = time.monotonic()
    first_token_at: float | None = None
    for chunk in client.stream("Count from one to fifteen in words, one per line.", max_output_tokens=200):
        if first_token_at is None:
            first_token_at = time.monotonic() - started
        print(chunk, end="", flush=True)
    print(f"\n[first text after {first_token_at or 0:.2f}s, total {time.monotonic() - started:.2f}s]\n")

    print("--- a bad request is not retried ---")
    try:
        GeminiClient(model="gemini-does-not-exist").complete("hello")
    except LLMBadRequest as err:
        print(f"LLMBadRequest status={err.status_code}: {err}")

    print("\n--- truncation is reported, not hidden ---")
    try:
        client.complete("Write three paragraphs about the sea.", max_output_tokens=15)
    except LLMTruncated as err:
        print(f"LLMTruncated: {err}")


if __name__ == "__main__":
    main()
