"""Offline tests for chapter 22. Copy to ai-course/tests/test_ch22.py and run: uv run pytest -q"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ch11.llm_client import FakeClient
from ch19.agent import AgentState, dispatch, run_agent
from ch19.research_tools import make_tools
from ch22.report import render, summarize
from ch22.traced_agent import TracingAgentBackend, traced_tools
from ch22.tracing import (
    PRICES,
    Tracer,
    TracingClient,
    estimate_cost,
    fingerprint,
    read_spans,
)


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        self.now += 0.25
        return self.now


def test_spans_nest_and_record_errors(tmp_path: Path) -> None:
    tracer = Tracer(tmp_path / "t.jsonl", trace_id="run1", clock=Clock())
    with tracer.span("pipeline") as outer:
        with tracer.span("stage-a", items=3):
            pass
        with pytest.raises(ValueError), tracer.span("stage-b"):
            raise ValueError("boom")
        tracer.event("note", "something happened")
    spans = read_spans(tracer.path)
    assert [s["name"] for s in spans] == ["stage-a", "stage-b", "note", "pipeline"]  # children close first
    assert all(s["trace_id"] == "run1" for s in spans)
    assert spans[0]["parent_id"] == outer.span_id and spans[3]["parent_id"] is None
    assert spans[1]["status"] == "error" and spans[1]["error"].startswith("ValueError") and spans[0]["items"] == 3
    assert spans[2]["kind"] == "event" and spans[2]["duration_ms"] == 0.0 and spans[0]["duration_ms"] == 250.0


def test_tracing_client_records_tokens_cost_and_no_text_by_default(tmp_path: Path) -> None:
    tracer = Tracer(tmp_path / "t.jsonl", clock=Clock())
    fake = FakeClient(script=["twelve chars", "streamed answer"])
    client = TracingClient(fake, tracer, model="gemini-3.5-flash-lite", stage="summarize")
    completion = client.complete("a secret prompt about a person", max_output_tokens=50)
    assert completion.text == "twelve chars"
    assert "".join(client.stream("another prompt")) == "streamed answer"
    spans = read_spans(tracer.path)
    llm = spans[0]
    assert llm["kind"] == "llm" and llm["name"] == "summarize" and llm["model"] == "gemini-3.5-flash-lite"
    assert llm["input_tokens"] == completion.input_tokens and llm["output_tokens"] == completion.output_tokens
    assert llm["cost_usd"] == round(estimate_cost("gemini-3.5-flash-lite", completion.input_tokens, completion.output_tokens), 6)
    assert "prompt" not in llm and llm["prompt_chars"] == len("a secret prompt about a person") and len(llm["prompt_sha256"]) == 16
    assert "secret" not in json.dumps(spans) and "completion_sha256" in llm
    assert spans[1]["streamed"] is True and spans[1]["chunks"] == 3 and spans[1]["ttft_ms"] > 0

    verbose = Tracer(tmp_path / "v.jsonl", record_text=True)
    TracingClient(FakeClient(script=["ok"]), verbose, model="gemini-3.5-flash-lite").complete("visible prompt")
    assert read_spans(verbose.path)[0]["prompt"] == "visible prompt"
    assert fingerprint("abc") == {"chars": 3, "sha256": fingerprint("abc")["sha256"]} and fingerprint("abc") != fingerprint("abd")


def test_report_aggregates_per_span_name(tmp_path: Path) -> None:
    tracer = Tracer(tmp_path / "t.jsonl", clock=Clock())
    client = TracingClient(FakeClient(script=["a", "b", "c"]), tracer, model="gemini-3.5-flash-lite", stage="summarize")
    for prompt in ("one", "two", "three"):
        client.complete(prompt)
    with pytest.raises(RuntimeError), tracer.span("fetch", "tool", tool="fetch_url"):
        raise RuntimeError("404")
    TracingClient(FakeClient(script=["z"]), tracer, model="mystery-model", stage="rerank").complete("x")
    spans = read_spans(tracer.path)
    summary = summarize(spans)
    assert summary["llm:summarize"]["calls"] == 3 and summary["llm:summarize"]["errors"] == 0 and summary["llm:summarize"]["p95_ms"] >= summary["llm:summarize"]["p50_ms"]
    assert summary["tool:fetch"]["errors"] == 1 and summary["llm:rerank"]["unpriced_models"] == ["mystery-model"]
    text = render(spans, "r")
    assert "| llm:summarize | 3 | 0 |" in text and "No price known for: mystery-model" in text and "## Errors" in text


def test_traced_agent_backend_and_tools(tmp_path: Path) -> None:
    tracer = Tracer(tmp_path / "t.jsonl", clock=Clock())

    class FakeBackend:
        def __init__(self) -> None:
            self.calls = 0

        def create(self, *, history, tools, system):
            self.calls += 1
            usage = SimpleNamespace(total_input_tokens=100, total_output_tokens=20)
            if self.calls == 1:
                return SimpleNamespace(steps=[SimpleNamespace(type="function_call", id="c1", name="search_feeds", arguments={"query": "rust"})], output_text="", usage=usage)
            return SimpleNamespace(steps=[], output_text="done", usage=usage)

    tools = traced_tools(make_tools(), tracer)
    state = run_agent(TracingAgentBackend(FakeBackend(), tracer, model="gemini-3.8-flash"), tools, AgentState("q"))
    assert state.stop_reason == "answered"
    spans = read_spans(tracer.path)
    names = [s["name"] for s in spans]
    assert names == ["agent.model", "tool.search_feeds", "agent.model"]
    assert spans[0]["tool_calls"] == ["search_feeds"] and spans[0]["cost_usd"] == round(estimate_cost("gemini-3.8-flash", 100, 20), 6)
    assert spans[1]["argument_keys"] == ["max_results", "query"] and spans[1]["result_chars"] > 0 and "Cargo" not in json.dumps(spans)  # defaults are filled in by the args model
    _, is_error = dispatch(tools, "read_item", {"item_id": "nope"})
    assert is_error and read_spans(tracer.path)[-1]["status"] == "error"
    assert set(PRICES) >= {"gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-embedding-2"}
