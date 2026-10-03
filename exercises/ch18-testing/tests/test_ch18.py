"""Offline tests for chapter 18. Copy to ai-course/tests/test_ch18.py and run: uv run pytest -q"""

from __future__ import annotations

import random
from pathlib import Path

import pytest
from conftest import live_enabled

from ch11.llm_client import FakeClient
from ch18.contracts import SnapshotMismatch, assert_matches_snapshot
from ch18.properties import (
    article_summary_violations,
    grounded_answer_violations,
    parses_as_json,
    random_article_summary,
)
from ch18.recorder import (
    Cassette,
    CassetteMiss,
    RecordingClient,
    ReplayClient,
    request_key,
)


def test_request_key_is_stable_and_sensitive() -> None:
    a = request_key("p", "s", {"type": "text"}, 100, 0.0)
    assert a == request_key("p", "s", {"type": "text"}, 100, 0.0) and len(a) == 24
    assert a != request_key("p!", "s", {"type": "text"}, 100, 0.0) and a != request_key("p", "s", None, 100, 0.0) and a != request_key("p", "s", {"type": "text"}, 100, 0.5)


def test_recording_then_replaying(tmp_path: Path) -> None:
    cassette_path = tmp_path / "cassettes" / "demo.jsonl"
    inner = FakeClient(script=["first answer", "second answer"])
    recorder = RecordingClient(inner, Cassette(cassette_path))
    assert recorder.complete("hello", system="sys").text == "first answer"
    assert recorder.complete("hello", system="sys").text == "first answer"  # same request: replayed, inner not called
    assert recorder.recorded == 1 and recorder.replayed == 1 and len(inner.calls) == 1
    assert recorder.complete("other").text == "second answer" and recorder.recorded == 2

    replay = ReplayClient(Cassette(cassette_path))
    assert replay.complete("hello", system="sys").text == "first answer" and replay.replayed == 1
    assert "".join(replay.stream("other")) == "second answer"
    with pytest.raises(CassetteMiss, match="AI_COURSE_RECORD=1"):
        replay.complete("never recorded")


def test_snapshot_lifecycle(tmp_path: Path) -> None:
    value = {"b": 2, "a": [1, 2]}
    assert assert_matches_snapshot("thing", value, tmp_path, update=False) == "created"
    assert assert_matches_snapshot("thing", {"a": [1, 2], "b": 2}, tmp_path, update=False) == "matched"  # key order does not matter
    with pytest.raises(SnapshotMismatch, match="drifted"):
        assert_matches_snapshot("thing", {"a": [1, 2], "b": 3}, tmp_path, update=False)
    assert assert_matches_snapshot("thing", {"a": [1, 2], "b": 3}, tmp_path, update=True) == "updated"
    assert assert_matches_snapshot("thing", {"a": [1, 2], "b": 3}, tmp_path, update=False) == "matched"


def test_property_checkers() -> None:
    for seed in range(20):
        rng = random.Random(seed)
        assert article_summary_violations(random_article_summary(rng, valid=True)) == []
        assert article_summary_violations(random_article_summary(rng, valid=False))
    assert grounded_answer_violations({"answer": "x", "citations": [1, 2], "supported": True}, n_sources=3) == []
    assert "citations within 1..n_sources" in grounded_answer_violations({"answer": "x", "citations": [4], "supported": True}, n_sources=3)
    assert "supported answers cite something" in grounded_answer_violations({"answer": "x", "citations": [], "supported": True}, n_sources=3)
    assert "unsupported answers are empty" in grounded_answer_violations({"answer": "x", "citations": [], "supported": False}, n_sources=3)
    assert parses_as_json('{"a": 1}') and not parses_as_json("nope")


def test_live_tier_decision() -> None:
    assert live_enabled(False, True) == (False, "live tests run only with --live")
    assert live_enabled(True, False)[0] is False and "GEMINI_API_KEY" in live_enabled(True, False)[1]
    assert live_enabled(True, True) == (True, "")
