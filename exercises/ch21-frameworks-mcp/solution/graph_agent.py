r"""Chapter 21 solution: the research agent as a LangGraph StateGraph with a checkpointer and an approval interrupt.

    research  -> review (interrupt: show the draft, wait for a decision) -> send | discard

    uv run --env-file .env python -m ch21.graph_agent "What changed in Kubernetes 1.36?"      # runs until the interrupt
    uv run --env-file .env python -m ch21.graph_agent --thread <id> --approve                   # resumes and sends
    uv run --env-file .env python -m ch21.graph_agent --thread <id> --reject
"""

from __future__ import annotations

import json
import sqlite3
import sys
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

ResearchFn = Callable[[str], tuple[str, list[str]]]  # question -> (draft answer, sources)
DeliverFn = Callable[[str, list[str]], str]  # (draft, sources) -> delivery receipt


class ReviewState(TypedDict, total=False):
    question: str
    draft: str
    sources: list[str]
    approved: bool
    delivered: str


def build_graph(research: ResearchFn, deliver: DeliverFn, checkpointer: Any):
    def research_node(state: ReviewState) -> ReviewState:
        draft, sources = research(state["question"])
        return {"draft": draft, "sources": sources}

    def review_node(state: ReviewState) -> ReviewState:
        # Execution stops here. The payload is what the human sees; the resume value is what they decide.
        decision = interrupt({"draft": state["draft"], "sources": state["sources"]})
        return {"approved": bool(decision)}

    def send_node(state: ReviewState) -> ReviewState:
        return {"delivered": deliver(state["draft"], state["sources"])}

    def discard_node(state: ReviewState) -> ReviewState:
        return {"delivered": "discarded"}

    graph = StateGraph(ReviewState)
    graph.add_node("research", research_node)
    graph.add_node("review", review_node)
    graph.add_node("send", send_node)
    graph.add_node("discard", discard_node)
    graph.add_edge(START, "research")
    graph.add_edge("research", "review")
    graph.add_conditional_edges("review", lambda s: "send" if s.get("approved") else "discard", {"send": "send", "discard": "discard"})
    graph.add_edge("send", END)
    graph.add_edge("discard", END)
    return graph.compile(checkpointer=checkpointer)


def open_checkpointer(path: Path) -> SqliteSaver:
    path.parent.mkdir(parents=True, exist_ok=True)
    return SqliteSaver(sqlite3.connect(str(path), check_same_thread=False))


def config_for(thread_id: str) -> dict[str, Any]:
    return {"configurable": {"thread_id": thread_id}}


def start_run(app: Any, question: str, thread_id: str) -> dict[str, Any]:
    """Run until the review interrupt. Returns the interrupt payload (draft + sources)."""
    result = app.invoke({"question": question}, config_for(thread_id))
    interrupts = result.get("__interrupt__", [])
    return interrupts[0].value if interrupts else {}


def resume_run(app: Any, thread_id: str, approved: bool) -> dict[str, Any]:
    """Continue the paused thread with the human decision. Returns the final state values."""
    return app.invoke(Command(resume=approved), config_for(thread_id))


def deliver_to_outbox(outbox: Path) -> DeliverFn:
    outbox.mkdir(parents=True, exist_ok=True)

    def deliver(draft: str, sources: list[str]) -> str:
        path = outbox / f"brief-{uuid.uuid4().hex[:8]}.md"
        path.write_text(draft + "\n\nSources: " + ", ".join(sources) + "\n", encoding="utf-8")
        return str(path)

    return deliver


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    from ch19.agent import AgentState, Budgets, run_agent
    from ch19.gemini_backend import GeminiAgentBackend
    from ch19.research_tools import make_tools

    def research_with_agent(question: str) -> tuple[str, list[str]]:
        final = run_agent(GeminiAgentBackend(), make_tools(), AgentState(question), Budgets(max_steps=6))
        return final.answer, final.sources

    state_dir = Path(__file__).parent / "state"
    app = build_graph(
        research=research_with_agent,
        deliver=deliver_to_outbox(state_dir / "outbox"),
        checkpointer=open_checkpointer(state_dir / "graph.sqlite"),
    )
    if "--thread" in argv:
        thread_id = argv[argv.index("--thread") + 1]
        final = resume_run(app, thread_id, approved="--approve" in argv)
        print(f"thread {thread_id}: delivered = {final.get('delivered')}")
        return 0
    question = " ".join(a for a in argv if not a.startswith("--")) or "What changed in Kubernetes 1.36 and what should operators do?"
    thread_id = uuid.uuid4().hex[:8]
    payload = start_run(app, question, thread_id)
    print(f"thread {thread_id} is waiting for review.\n\n{payload.get('draft')}\n\nsources: {payload.get('sources')}")
    print(f"\nresume with:  python -m ch21.graph_agent --thread {thread_id} --approve   (or --reject)")
    print("state:", json.dumps(app.get_state(config_for(thread_id)).values, ensure_ascii=False)[:200], "| next:", app.get_state(config_for(thread_id)).next)
    return 0


if __name__ == "__main__":
    sys.exit(main())
