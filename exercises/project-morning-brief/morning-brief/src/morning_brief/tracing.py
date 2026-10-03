"""Tracer (JSONL spans per run), prices and cost estimation. No prompt text is recorded by default."""

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

# USD per 1M tokens: (input, output, cached input). Paid tier; the free tier bills nothing.
PRICES: dict[str, tuple[float, float, float]] = {
    "gemini-3.5-flash-lite": (0.30, 2.50, 0.03),
    "gemini-3.8-flash": (0.75, 3.75, 0.075),
    "gemini-embedding-2": (0.20, 0.0, 0.20),
}


def estimate_cost(model: str, input_tokens: float, output_tokens: float, *, cached_tokens: float = 0.0) -> float:
    prices = PRICES.get(model)
    if prices is None:
        return 0.0
    price_in, price_out, price_cached = prices
    return (input_tokens * price_in + output_tokens * price_out + cached_tokens * price_cached) / 1_000_000


def fingerprint(text: str) -> dict[str, Any]:
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

    def as_dict(self) -> dict[str, Any]:
        duration = None if self.ended_at is None else round((self.ended_at - self.started_at) * 1000, 1)
        return {"trace_id": self.trace_id, "span_id": self.span_id, "parent_id": self.parent_id, "name": self.name, "kind": self.kind, "started_at": self.started_at, "duration_ms": duration, "status": self.status, **self.attributes}


class Tracer:
    def __init__(self, path: Path | str, *, trace_id: str | None = None, record_text: bool = False) -> None:
        self.path = Path(path)
        self.trace_id = trace_id or uuid.uuid4().hex[:12]
        self.record_text = record_text
        self._stack: list[Span] = []
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, span: Span) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(span.as_dict(), ensure_ascii=False, default=str) + "\n")

    @contextmanager
    def span(self, name: str, kind: str = "stage", **attributes: Any) -> Iterator[Span]:
        parent = self._stack[-1].span_id if self._stack else None
        span = Span(self.trace_id, uuid.uuid4().hex[:8], parent, name, kind, time.time(), attributes=attributes)
        self._stack.append(span)
        try:
            yield span
        except Exception as exc:
            span.status = "error"
            span.attributes["error"] = f"{type(exc).__name__}: {exc}"[:200]
            raise
        finally:
            span.ended_at = time.time()
            self._stack.pop()
            self._write(span)

    def event(self, name: str, detail: str = "", **attributes: Any) -> None:
        now = time.time()
        parent = self._stack[-1].span_id if self._stack else None
        self._write(Span(self.trace_id, uuid.uuid4().hex[:8], parent, name, "event", now, now, attributes={"detail": detail[:300], **attributes}))

    def text_attributes(self, prefix: str, text: str) -> dict[str, Any]:
        return {prefix: text} if self.record_text else {f"{prefix}_{k}": v for k, v in fingerprint(text).items()}


def read_spans(path: Path | str) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
