"""Chapter 22 starter: a tracer you own. One JSONL line per span; no raw text unless you ask for it.

    log     a line that says what happened ("fetched 20 items")
    metric  a number over time (p95 latency, cost per day)
    trace   the tree of spans for ONE run: which stage, which call, how long, how much

Spans carry: trace_id (the run), span_id, parent_id, name, kind (stage | llm | tool | event), timing,
and attributes: model, tokens (input / output / cached), estimated cost, status, tool name, errors.
Prompts and completions are recorded as length + hash by default. Redaction is a design decision.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ch11.llm_client import Completion, LLMClient

# USD per 1M tokens: (input, output, cached-input). Paid tier, from the Stage 1 price table; free tier = 0.
# Unknown models cost 0.0 and are flagged in the report instead of being guessed.
PRICES: dict[str, tuple[float, float, float]] = {
    "gemini-3.5-flash-lite": (0.30, 2.50, 0.075),
    "gemini-3.8-flash": (0.75, 3.75, 0.1875),
    "gemini-embedding-2": (0.20, 0.0, 0.20),
}


def estimate_cost(model: str, input_tokens: float, output_tokens: float, *, cached_tokens: float = 0.0) -> float:
    """Paid-tier estimate in USD. `input_tokens` excludes the cached part; pass it in `cached_tokens`."""
    prices = PRICES.get(model)
    if prices is None:
        return 0.0
    price_in, price_out, price_cached = prices
    return (input_tokens * price_in + output_tokens * price_out + cached_tokens * price_cached) / 1_000_000


def fingerprint(text: str) -> dict[str, Any]:
    """What we keep instead of the text: enough to detect repeats and sizes, not enough to read it."""
    return {"chars": len(text), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]}


@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_id: str | None
    name: str
    kind: str
    started_at: float
    ended_at: float | None = None
    status: str = "ok"
    attributes: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float | None:
        return None if self.ended_at is None else round((self.ended_at - self.started_at) * 1000, 1)

    def as_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id, "span_id": self.span_id, "parent_id": self.parent_id, "name": self.name, "kind": self.kind,
            "started_at": self.started_at, "duration_ms": self.duration_ms, "status": self.status, **self.attributes,
        }


class Tracer:
    """Writes spans for one trace (one run) to a JSONL file. Nesting comes from `with tracer.span(...)`."""

    def __init__(self, path: Path | str, *, trace_id: str | None = None, record_text: bool = False, clock=time.time) -> None:
        self.path = Path(path)
        self.trace_id = trace_id or uuid.uuid4().hex[:12]
        self.record_text = record_text
        self.clock = clock
        self._stack: list[Span] = []
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def current(self) -> Span | None:
        return self._stack[-1] if self._stack else None

    def _write(self, span: Span) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(span.as_dict(), ensure_ascii=False, default=str) + "\n")

    @contextmanager
    def span(self, name: str, kind: str = "stage", **attributes: Any) -> Iterator[Span]:
        # TODO 1: create a Span (parent = the current span's id, if any), push it on the stack, yield it;
        # on an exception set status "error" and attributes["error"] (type: message, truncated) and re-raise;
        # in `finally` set ended_at, pop the stack and write the span.
        raise NotImplementedError
        yield  # keeps the generator shape for the context manager

    def event(self, name: str, detail: str = "", **attributes: Any) -> None:
        """A zero-duration span: something happened that is worth a line."""
        now = self.clock()
        self._write(Span(self.trace_id, uuid.uuid4().hex[:8], self.current.span_id if self.current else None, name, "event", now, now, attributes={"detail": detail[:300], **attributes}))

    def text_attributes(self, prefix: str, text: str) -> dict[str, Any]:
        if self.record_text:
            return {prefix: text}
        return {f"{prefix}_{k}": v for k, v in fingerprint(text).items()}


class TracingClient:
    """Wraps any LLMClient: every complete() becomes an llm span with tokens, cost, status and latency."""

    def __init__(self, inner: LLMClient, tracer: Tracer, *, model: str, stage: str = "llm") -> None:
        self.inner = inner
        self.tracer = tracer
        self.model = model
        self.stage = stage

    def complete(self, prompt: str, *, system: str | None = None, max_output_tokens: int = 1024, temperature: float = 0.2, response_format: dict[str, Any] | None = None) -> Completion:
        # TODO 2: open an llm span (model, max_output_tokens, temperature, structured flag, prompt fingerprint via
        # self.tracer.text_attributes("prompt", prompt)); call the inner client; record input/output/cached tokens,
        # attempts, completion_status, cost_usd (estimate_cost with cached tokens separated) and the completion
        # fingerprint; return the completion.
        raise NotImplementedError

    def stream(self, prompt: str, *, system: str | None = None, max_output_tokens: int = 1024) -> Iterator[str]:
        with self.tracer.span(self.stage, "llm", model=self.model, streamed=True, **self.tracer.text_attributes("prompt", prompt)) as span:
            first_at: float | None = None
            chunks = 0
            for chunk in self.inner.stream(prompt, system=system, max_output_tokens=max_output_tokens):
                if first_at is None:
                    first_at = self.tracer.clock()
                    span.attributes["ttft_ms"] = round((first_at - span.started_at) * 1000, 1)
                chunks += 1
                yield chunk
            span.attributes["chunks"] = chunks


def read_spans(path: Path | str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
