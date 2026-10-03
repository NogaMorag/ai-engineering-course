"""Offline tests for chapter 10. Copy to ai-course/tests/test_ch10.py and run: uv run pytest -q"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ch10 import tools
from ch10.tool_loop import ToolLoopExceeded, run
from ch10.tools import dispatch, tool_declarations, validate_public_http_url


def interaction(id: str, steps: list | None = None, text: str = "", status: str = "completed") -> SimpleNamespace:
    usage = SimpleNamespace(total_input_tokens=10, total_output_tokens=5)
    return SimpleNamespace(id=id, steps=steps or [], output_text=text, status=status, usage=usage)


def call(id: str, name: str, arguments: dict) -> SimpleNamespace:
    return SimpleNamespace(type="function_call", id=id, name=name, arguments=arguments)


class FakeBackend:
    def __init__(self, scripted: list[SimpleNamespace]) -> None:
        self.scripted = list(scripted)
        self.inputs: list = []
        self.previous_ids: list = []

    def create(self, *, input, previous_interaction_id=None):
        self.inputs.append(input)
        self.previous_ids.append(previous_interaction_id)
        return self.scripted.pop(0)


@pytest.fixture
def notes_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "a.md").write_text("Temperature divides the logits before softmax.\nSeeds make repeats likely.\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("Lower TEMPERATURE sharpens the distribution.\n", encoding="utf-8")
    monkeypatch.setattr(tools, "NOTES_DIR", tmp_path)
    return tmp_path


def test_url_validation_blocks_non_http_and_private_hosts() -> None:
    assert validate_public_http_url("https://example.com/a") == "https://example.com/a"
    for bad in ("file:///etc/passwd", "ftp://example.com", "http://localhost:8000", "http://127.0.0.1/", "http://10.1.2.3/", "http://192.168.1.1/", "http://172.20.0.1/", "http://box.internal/"):
        with pytest.raises(ValueError):
            validate_public_http_url(bad)


def test_search_notes_is_case_insensitive_and_bounded(notes_dir: Path) -> None:
    result = tools.search_notes("temperature", max_results=1)
    assert result["matches"][0]["file"] == "a.md" and result["more"] is True
    assert len(tools.search_notes("temperature")["matches"]) == 2


def test_dispatch_rejects_unknown_tool_and_invalid_arguments(notes_dir: Path) -> None:
    text, is_error = dispatch("delete_everything", {})
    assert is_error and "unknown tool" in text
    text, is_error = dispatch("search_notes", {"query": "x", "max_results": 50})
    assert is_error and "invalid arguments" in text
    text, is_error = dispatch("fetch_url", {"url": "file:///etc/passwd"})
    assert is_error and "only http" in text


def test_dispatch_runs_a_valid_call_and_returns_json(notes_dir: Path) -> None:
    text, is_error = dispatch("search_notes", {"query": "seeds"})
    assert not is_error
    assert json.loads(text)["matches"][0]["text"].startswith("Seeds")


def test_declarations_have_schema_without_titles() -> None:
    declarations = tool_declarations()
    assert {d["name"] for d in declarations} == {"fetch_url", "search_notes"}
    for declaration in declarations:
        assert declaration["type"] == "function"
        assert '"title"' not in json.dumps(declaration["parameters"])
        assert "properties" in declaration["parameters"]


def test_loop_executes_a_call_and_returns_the_final_answer(notes_dir: Path) -> None:
    backend = FakeBackend([
        interaction("i1", steps=[call("c1", "search_notes", {"query": "temperature"})]),
        interaction("i2", text="Your notes say temperature divides the logits."),
    ])
    outcome = run(backend, "What do my notes say about temperature?")
    assert outcome.text.startswith("Your notes say")
    assert outcome.rounds == 2 and len(outcome.tool_calls) == 1 and not outcome.tool_calls[0].is_error
    sent = backend.inputs[1]
    assert sent[0]["type"] == "function_result" and sent[0]["call_id"] == "c1"
    assert backend.previous_ids[1] == "i1"
    assert "logits" in sent[0]["result"]


def test_loop_returns_all_parallel_results_in_one_message(notes_dir: Path) -> None:
    backend = FakeBackend([
        interaction("i1", steps=[call("c1", "search_notes", {"query": "temperature"}), call("c2", "nope", {})]),
        interaction("i2", text="done"),
    ])
    outcome = run(backend, "two things")
    sent = backend.inputs[1]
    assert [item["call_id"] for item in sent] == ["c1", "c2"]
    assert sent[1]["is_error"] is True
    assert [c.is_error for c in outcome.tool_calls] == [False, True]


def test_loop_stops_after_max_rounds(notes_dir: Path) -> None:
    looping = [interaction(f"i{n}", steps=[call(f"c{n}", "search_notes", {"query": "x"})]) for n in range(6)]
    with pytest.raises(ToolLoopExceeded):
        run(FakeBackend(looping), "loop forever", max_rounds=3)
