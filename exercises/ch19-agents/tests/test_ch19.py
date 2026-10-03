"""Offline tests for chapter 19. Copy to ai-course/tests/test_ch19.py and run: uv run pytest -q"""

from __future__ import annotations

import json
import threading
import time
from types import SimpleNamespace

from ch11.llm_client import FakeClient
from ch19.agent import AgentState, Budgets, dispatch, run_agent
from ch19.patterns import PROMPT_BY_KIND, run_parallel, summarize_routed
from ch19.research_tools import load_feeds, make_tools


def interaction(steps=None, text="", tokens=(100, 20)):
    return SimpleNamespace(steps=steps or [], output_text=text, usage=SimpleNamespace(total_input_tokens=tokens[0], total_output_tokens=tokens[1]))


def call(cid, name, arguments):
    return SimpleNamespace(type="function_call", id=cid, name=name, arguments=arguments)


class FakeBackend:
    def __init__(self, scripted):
        self.scripted = list(scripted)
        self.histories = []

    def create(self, *, history, tools, system):
        self.histories.append([dict(s) for s in history])
        item = self.scripted.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


def test_routing_picks_the_prompt_for_the_kind() -> None:
    fake = FakeClient(script=[json.dumps({"kind": "incident_postmortem"}), "- trigger\n- impact\n- fixes"])
    kind, summary = summarize_routed(fake, "A long transaction took the database down.")
    assert kind == "incident_postmortem" and summary.startswith("- trigger")
    assert fake.calls[1]["system"] == PROMPT_BY_KIND["incident_postmortem"]


def test_parallel_map_bounds_concurrency_and_keeps_order() -> None:
    lock, active, peak = threading.Lock(), [0], [0]

    def work(n: int) -> int:
        with lock:
            active[0] += 1
            peak[0] = max(peak[0], active[0])
        time.sleep(0.03)
        with lock:
            active[0] -= 1
        return n * n

    assert run_parallel(work, range(9), concurrency=3) == [n * n for n in range(9)]
    assert 2 <= peak[0] <= 3


def test_research_tools_search_read_and_errors() -> None:
    tools = make_tools()
    assert set(tools) == {"search_feeds", "read_item"} and "fetch_url" in make_tools(allow_network=True)
    text, is_error = dispatch(tools, "search_feeds", {"query": "kubernetes networking"})
    result = json.loads(text)
    assert not is_error and result["results"][0]["id"] == "f03"
    text, is_error = dispatch(tools, "read_item", {"item_id": "f03"})
    assert not is_error and "legacy CNI" in json.loads(text)["text"]
    text, is_error = dispatch(tools, "read_item", {"item_id": "nope"})
    assert is_error and "KeyError" in text
    assert len(load_feeds()) == 20


def test_agent_loop_answers_with_sources_and_a_trace() -> None:
    backend = FakeBackend([
        interaction([call("c1", "search_feeds", {"query": "rust compile"})]),
        interaction([call("c2", "read_item", {"item_id": "f01"}), call("c3", "read_item", {"item_id": "f02"})]),
        interaction(text="Builds are slow; a shared cache helps (f01, f02)."),
    ])
    state = run_agent(backend, make_tools(), AgentState("why are rust builds slow?"), Budgets(max_steps=6))
    assert state.stop_reason == "answered" and state.steps == 3 and state.sources == ["f01", "f02"]
    assert state.answer.startswith("Builds are slow") and state.tokens == 360
    kinds = [t.kind for t in state.trace]
    assert kinds == ["model", "tool", "model", "tool", "tool", "model"]
    types_ = [s["type"] for s in state.history]
    assert types_ == ["user_input", "function_call", "function_result", "function_call", "function_call", "function_result", "function_result", "model_output"]
    assert backend.histories[1][-1]["type"] == "function_result" and backend.histories[1][-1]["call_id"] == "c1"
    restored = AgentState.from_json(state.to_json())
    assert restored.answer == state.answer and restored.trace[0].kind == "model"


def test_budgets_stop_the_loop_with_a_reason() -> None:
    forever = [interaction([call(f"c{i}", "search_feeds", {"query": f"q{i}"})]) for i in range(10)]
    assert run_agent(FakeBackend(forever), make_tools(), AgentState("q"), Budgets(max_steps=2)).stop_reason == "max_steps"
    ticks = iter([0.0, 0.0, 50.0, 50.0, 100.0, 100.0, 100.0, 100.0])
    slow = run_agent(FakeBackend(list(forever)), make_tools(), AgentState("q"), Budgets(max_steps=9, max_seconds=60), clock=lambda: next(ticks))
    assert slow.stop_reason == "timeout"
    assert run_agent(FakeBackend(list(forever)), make_tools(), AgentState("q"), Budgets(max_steps=9, max_tokens=200)).stop_reason == "token_budget"
    assert run_agent(FakeBackend([RuntimeError("boom")]), make_tools(), AgentState("q")).stop_reason == "error"
    vetoed = run_agent(FakeBackend(list(forever)), make_tools(), AgentState("q"), guard=lambda state, proposed: "loop_detected")
    assert vetoed.stop_reason == "loop_detected" and "Stopped before answering" in vetoed.answer


def test_on_step_runs_after_every_completed_round() -> None:
    seen = []
    backend = FakeBackend([interaction([call("c1", "search_feeds", {"query": "solar"})]), interaction(text="done")])
    run_agent(backend, make_tools(), AgentState("q"), on_step=lambda s: seen.append((s.steps, len(s.history))))
    assert seen == [(1, 3), (2, 4)]
    exhausted = run_agent(FakeBackend([]), make_tools(), AgentState("q"))  # the fake raises IndexError
    assert exhausted.stop_reason == "error" and "IndexError" in exhausted.trace[-1].detail["error"]
