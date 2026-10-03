"""Chapter 18 starter: record once, replay forever. A cassette of LLM completions keyed by the exact request.

    AI_COURSE_RECORD=1 uv run --env-file .env pytest tests/test_live_recorded.py   # records misses
    uv run pytest                                                                 # replays, no key, no network
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterator
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ch11.llm_client import Completion, LLMClient


class CassetteMiss(Exception):
    """The request is not in the cassette. Re-record, or fix the test so it sends the recorded request."""


def request_key(prompt: str, system: str | None, response_format: dict[str, Any] | None, max_output_tokens: int, temperature: float) -> str:
    payload = json.dumps({"p": prompt, "s": system, "rf": response_format, "m": max_output_tokens, "t": temperature}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


class Cassette:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.entries: dict[str, dict[str, Any]] = {}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    entry = json.loads(line)
                    self.entries[entry["key"]] = entry

    def get(self, key: str) -> dict[str, Any] | None:
        return self.entries.get(key)

    def put(self, key: str, *, prompt_preview: str, completion: Completion) -> None:
        entry = {"key": key, "prompt_preview": prompt_preview[:120], "completion": asdict(completion)}
        self.entries[key] = entry
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


class ReplayClient:
    """Serves recorded completions. Any unrecorded request is a loud failure, never a silent network call."""

    def __init__(self, cassette: Cassette) -> None:
        self.cassette = cassette
        self.replayed = 0

    def complete(self, prompt: str, *, system: str | None = None, max_output_tokens: int = 1024, temperature: float = 0.2, response_format: dict[str, Any] | None = None) -> Completion:
        key = request_key(prompt, system, response_format, max_output_tokens, temperature)
        entry = self.cassette.get(key)
        if entry is None:
            raise CassetteMiss(f"no recording for key {key} (prompt starts: {prompt[:60]!r}). Run with AI_COURSE_RECORD=1 to record it.")
        self.replayed += 1
        return Completion(**entry["completion"])

    def stream(self, prompt: str, *, system: str | None = None, max_output_tokens: int = 1024) -> Iterator[str]:
        text = self.complete(prompt, system=system, max_output_tokens=max_output_tokens, temperature=0.2).text
        for i in range(0, len(text), 40):
            yield text[i : i + 40]


class RecordingClient:
    """Replays what it has, records what it has not. Wraps a real client; used only when recording."""

    def __init__(self, inner: LLMClient, cassette: Cassette) -> None:
        self.inner = inner
        self.cassette = cassette
        self.recorded = 0
        self.replayed = 0

    def complete(self, prompt: str, *, system: str | None = None, max_output_tokens: int = 1024, temperature: float = 0.2, response_format: dict[str, Any] | None = None) -> Completion:
        # TODO 1: compute the key; if the cassette has it, count a replay and return Completion(**entry["completion"]);
        # otherwise call self.inner.complete(...) with the same arguments, store it with cassette.put(...),
        # count a recording, and return it.
        raise NotImplementedError

    def stream(self, prompt: str, *, system: str | None = None, max_output_tokens: int = 1024) -> Iterator[str]:
        yield self.complete(prompt, system=system, max_output_tokens=max_output_tokens).text


def recording_enabled() -> bool:
    return os.environ.get("AI_COURSE_RECORD") == "1"


def client_for_tests(cassette_path: Path, real_client_factory=None) -> LLMClient:
    """Replay by default; record when AI_COURSE_RECORD=1 (and a real client factory is given)."""
    cassette = Cassette(cassette_path)
    if recording_enabled():
        if real_client_factory is None:
            from ch11.llm_client import GeminiClient

            real_client_factory = GeminiClient
        return RecordingClient(real_client_factory(), cassette)
    return ReplayClient(cassette)
