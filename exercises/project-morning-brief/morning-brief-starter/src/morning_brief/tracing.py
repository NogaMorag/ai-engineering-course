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
PRICES: dict[str, tuple[float, float, float]] = {'gemini-3.5-flash-lite': (0.3, 2.5, 0.075), 'gemini-3.8-flash': (0.75, 3.75, 0.1875), 'gemini-embedding-2': (0.2, 0.0, 0.2)}

def estimate_cost(model: str, input_tokens: float, output_tokens: float, *, cached_tokens: float=0.0) -> float:
    raise NotImplementedError

def fingerprint(text: str) -> dict[str, Any]:
    raise NotImplementedError

@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_id: str | None
    name: str
    kind: str
    started_at: float
    ended_at: float | None = None
    status: str = 'ok'
    attributes: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        raise NotImplementedError

class Tracer:

    def __init__(self, path: Path | str, *, trace_id: str | None=None, record_text: bool=False) -> None:
        raise NotImplementedError

    def _write(self, span: Span) -> None:
        raise NotImplementedError

    @contextmanager
    def span(self, name: str, kind: str='stage', **attributes: Any) -> Iterator[Span]:
        raise NotImplementedError

    def event(self, name: str, detail: str='', **attributes: Any) -> None:
        raise NotImplementedError

    def text_attributes(self, prefix: str, text: str) -> dict[str, Any]:
        raise NotImplementedError

def read_spans(path: Path | str) -> list[dict[str, Any]]:
    raise NotImplementedError
