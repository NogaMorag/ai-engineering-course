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

    def __init__(self, message: str, *, status_code: int | None=None) -> None:
        raise NotImplementedError

class LLMRateLimited(LLMError):
    retryable = True

class LLMUnavailable(LLMError):
    retryable = True

class LLMBadRequest(LLMError):
    pass

class LLMTruncated(LLMError):
    pass

def classify(exc: BaseException) -> LLMError:
    raise NotImplementedError

@dataclass
class Completion:
    text: str
    status: str
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    attempts: int = 1
    latency_s: float = 0.0
    model: str = ''

@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_delay_s: float = 1.0
    max_delay_s: float = 15.0
    total_deadline_s: float = 60.0

    def delay(self, attempt: int, rng: random.Random) -> float:
        raise NotImplementedError

def with_retries(operation: Callable[[], Completion], policy: RetryPolicy, *, sleep=time.sleep, clock=time.monotonic, rng: random.Random | None=None) -> Completion:
    raise NotImplementedError

class LLMClient(Protocol):
    model: str

    def complete(self, prompt: str, *, system: str | None=None, max_output_tokens: int=1024, temperature: float=0.2, response_format: dict[str, Any] | None=None) -> Completion:
        raise NotImplementedError

class GeminiClient:

    def __init__(self, model: str | None=None, *, timeout_s: float=60.0, policy: RetryPolicy | None=None, log: Callable[[str], None] | None=None) -> None:
        raise NotImplementedError

    def complete(self, prompt: str, *, system: str | None=None, max_output_tokens: int=1024, temperature: float=0.2, response_format: dict[str, Any] | None=None) -> Completion:
        raise NotImplementedError

@dataclass
class FakeClient:
    """Scripted answers (str) or failures (Exception) in order. `default` answers when the script runs out."""
    script: list[str | Exception] = field(default_factory=list)
    default: str | None = None
    model: str = 'fake-model'
    calls: list[dict[str, Any]] = field(default_factory=list)

    def complete(self, prompt: str, *, system: str | None=None, max_output_tokens: int=1024, temperature: float=0.2, response_format: dict[str, Any] | None=None) -> Completion:
        raise NotImplementedError

@dataclass
class Outcome:
    completion: Completion | None
    source: str
    errors: list[str] = field(default_factory=list)

def resilient_complete(primary: LLMClient, prompt: str, *, fallback: LLMClient | None=None, **kwargs: Any) -> Outcome:
    """Primary (with its own retries), then the fallback, then a degraded outcome. Every path is recorded."""
    raise NotImplementedError
