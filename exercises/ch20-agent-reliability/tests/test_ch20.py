"""Offline tests for chapter 20. Copy to ai-course/tests/test_ch20.py and run: uv run pytest -q"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ch11.llm_client import FakeClient
from ch19.agent import SYSTEM, AgentState, Budgets, dispatch
from ch19.research_tools import make_tools
from ch20.guardrails import (
    IdempotencyStore,
    LoopDetector,
    ScriptedApproval,
    gated,
    idempotent,
    make_send_email_tool,
)
from ch20.memory import (
    UserMemory,
    UserPreferences,
    summarize_history,
    system_with_memory,
)
from ch20.persistence import RunStore, run_with_checkpoints


def interaction(steps=None, text=""):
    return SimpleNamespace(steps=steps or [], output_text=text, usage=SimpleNamespace(total_input_tokens=10, total_output_tokens=5))


def call(cid, name, arguments):
    return SimpleNamespace(type="function_call", id=cid, name=name, arguments=arguments)


class SimulatedCrash(BaseException):
    """Not an Exception: the loop must not catch it, exactly like a killed process."""


class FakeBackend:
    def __init__(self, scripted):
        self.scripted = list(scripted)

    def create(self, *, history, tools, system):
        item = self.scripted.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


def test_loop_detector_vetoes_a_repeated_call() -> None:
    state = AgentState("q", history=[{"type": "user_input"}, {"type": "function_call", "id": "c1", "name": "search_feeds", "arguments": {"query": "rust"}}])
    detector = LoopDetector()
    assert detector(state, [("search_feeds", {"query": "rust"})]) == "loop_detected"
    assert detector(state, [("search_feeds", {"query": "python"})]) is None
    assert LoopDetector(max_repeats=2)(state, [("search_feeds", {"query": "rust"})]) is None


def test_approval_gate_turns_a_denial_into_an_error_result(tmp_path: Path) -> None:
    outbox = tmp_path / "outbox"
    gate = ScriptedApproval([False, True])
    tool = gated(make_send_email_tool(outbox), gate)
    tools = {"send_email": tool}
    text, is_error = dispatch(tools, "send_email", {"to": "me@example.com", "subject": "hi", "body": "x"})
    assert is_error and "not approved" in text and not list(outbox.glob("*.json"))
    text, is_error = dispatch(tools, "send_email", {"to": "me@example.com", "subject": "hi", "body": "x"})
    assert not is_error and json.loads(text)["status"] == "sent" and len(list(outbox.glob("*.json"))) == 1
    assert gate.asked[0][0] == "send_email" and gate.asked[0][1]["subject"] == "hi" and tool.side_effect


def test_idempotent_send_runs_the_side_effect_once(tmp_path: Path) -> None:
    store = IdempotencyStore(tmp_path / "idem.sqlite")
    tool = idempotent(make_send_email_tool(tmp_path / "outbox"), store)
    args = {"to": "me@example.com", "subject": "brief", "body": "text", "idempotency_key": "issue-2026-10-03"}
    first = json.loads(dispatch({"send_email": tool}, "send_email", args)[0])
    second = json.loads(dispatch({"send_email": tool}, "send_email", args)[0])
    assert first["status"] == "sent" and "replayed" not in first
    assert second["replayed"] is True and second["message_id"] == first["message_id"]
    assert len(list((tmp_path / "outbox").glob("*.json"))) == 1
    other = json.loads(dispatch({"send_email": tool}, "send_email", {**args, "idempotency_key": "issue-2026-10-04"})[0])
    assert other["message_id"] != first["message_id"] and len(list((tmp_path / "outbox").glob("*.json"))) == 2


def test_crash_then_resume_by_run_id(tmp_path: Path) -> None:
    store = RunStore(tmp_path / "runs.sqlite")
    tools = make_tools()
    crashing = FakeBackend([interaction([call("c1", "search_feeds", {"query": "kubernetes"})]), SimulatedCrash()])
    state = AgentState("what changed in kubernetes 1.36?")
    with pytest.raises(SimulatedCrash):
        run_with_checkpoints(crashing, tools, store, state=state, budgets=Budgets(max_steps=6))
    saved = store.load(state.run_id)
    assert saved is not None and saved.status == "running" and saved.steps == 1 and saved.history[-1]["type"] == "function_result"
    assert store.list_runs()[0]["run_id"] == state.run_id

    healthy = FakeBackend([interaction([call("c2", "read_item", {"item_id": "f03"})]), interaction(text="Legacy CNI clusters lost networking (f03).")])
    resumed = run_with_checkpoints(healthy, tools, store, resume_run_id=state.run_id, budgets=Budgets(max_steps=6))
    assert resumed.stop_reason == "answered" and resumed.steps == 3 and resumed.sources == ["f03"]
    assert store.load(state.run_id).status == "done"
    assert run_with_checkpoints(healthy, tools, store, resume_run_id=state.run_id).stop_reason == "answered"  # done runs are returned as is
    with pytest.raises(KeyError):
        run_with_checkpoints(healthy, tools, store, resume_run_id="missing")


def test_memory_changes_the_prompt_and_summaries_keep_the_tail(tmp_path: Path) -> None:
    memory = UserMemory(tmp_path / "prefs.json")
    assert memory.load() == UserPreferences()
    memory.save(UserPreferences(name="Noga", language="en", skip_topics=["sports", "crypto"], max_sentences=3))
    prefs = memory.load()
    system = system_with_memory(SYSTEM, prefs)
    assert "Answer in English, in at most 3 sentences." in system and "sports, crypto" in system and system.startswith(SYSTEM)

    history = [{"type": "user_input", "content": [{"type": "text", "text": "q"}]}] + [{"type": "function_result", "call_id": f"c{i}", "name": "read_item", "result": f"r{i}", "is_error": False} for i in range(8)]
    fake = FakeClient(script=["read f01 and f02: builds are slow"])
    compact = summarize_history(fake, history, keep_last=4)
    assert len(compact) == 6 and compact[0] == history[0] and compact[1]["type"] == "user_input" and "Summary of earlier" in compact[1]["content"][0]["text"]
    assert compact[-4:] == history[-4:] and "c3" in fake.calls[0]["prompt"]
    assert summarize_history(fake, history[:3], keep_last=4) == history[:3] and len(fake.calls) == 1
