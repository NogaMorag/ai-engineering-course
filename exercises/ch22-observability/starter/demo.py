r"""Chapter 22 starter, day 43: instrument the summarizer and the agent, then print the run report.

    uv run --env-file .env python -m ch22.demo
    uv run python -m ch22.report ch22\out\traces.jsonl
"""

from __future__ import annotations

import os
from pathlib import Path

from ch09.schemas import RESPONSE_FORMAT
from ch09.summarize_structured import SYSTEM, build_prompt
from ch11.llm_client import GeminiClient
from ch19.agent import AgentState, Budgets, run_agent
from ch19.gemini_backend import GeminiAgentBackend
from ch19.research_tools import load_feeds, make_tools
from ch22.report import render
from ch22.traced_agent import TracingAgentBackend, traced_tools
from ch22.tracing import Tracer, TracingClient, read_spans

OUT = Path(__file__).parent / "out"


def main() -> None:
    fast, smart = os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite"), os.environ.get("MODEL_SMART", "gemini-3.8-flash")
    tracer = Tracer(OUT / "traces.jsonl")
    feeds = load_feeds()

    with tracer.span("summarize-3-items"):
        client = TracingClient(GeminiClient(fast), tracer, model=fast, stage="summarize")
        for item in feeds[:3]:
            client.complete(build_prompt(item["text"]), system=SYSTEM, max_output_tokens=400, temperature=0.1, response_format=RESPONSE_FORMAT)

    with tracer.span("research-agent"):
        backend = TracingAgentBackend(GeminiAgentBackend(smart), tracer, model=smart)
        state = run_agent(backend, traced_tools(make_tools(), tracer), AgentState("What is slowing down Rust developers and what helps?"), Budgets(max_steps=6))
        tracer.event("agent_finished", f"{state.stop_reason} after {state.steps} calls", sources=state.sources)

    print(render(read_spans(tracer.path), f"run {tracer.trace_id}"))
    print(f"trace file: {tracer.path} (no article text inside; set record_text=True to change that)")


if __name__ == "__main__":
    main()
