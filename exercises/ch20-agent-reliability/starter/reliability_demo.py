"""Chapter 20 starter, days 38-39: the research agent with guardrails, checkpoints, resume and memory.

    uv run --env-file .env python -m ch20.reliability_demo "What changed in Kubernetes 1.36?"
    uv run --env-file .env python -m ch20.reliability_demo --resume <run_id>
    uv run --env-file .env python -m ch20.reliability_demo --list
"""

from __future__ import annotations

import sys
from pathlib import Path

from ch19.agent import SYSTEM, AgentState, Budgets
from ch19.gemini_backend import GeminiAgentBackend
from ch19.research_tools import make_tools
from ch20.guardrails import (
    ConsoleApproval,
    IdempotencyStore,
    LoopDetector,
    gated,
    idempotent,
    make_send_email_tool,
)
from ch20.memory import UserMemory, system_with_memory
from ch20.persistence import RunStore, run_with_checkpoints

STATE_DIR = Path(__file__).parent / "state"


def main() -> int:
    STATE_DIR.mkdir(exist_ok=True)
    store = RunStore(STATE_DIR / "runs.sqlite")
    if "--list" in sys.argv:
        for run in store.list_runs():
            print(run)
        return 0
    prefs = UserMemory(STATE_DIR / "preferences.json").load()
    tools = make_tools()
    tools["send_email"] = idempotent(gated(make_send_email_tool(STATE_DIR / "outbox"), ConsoleApproval()), IdempotencyStore(STATE_DIR / "idempotency.sqlite"))
    backend = GeminiAgentBackend()
    common = {"budgets": Budgets(max_steps=6, max_seconds=90, max_tokens=40_000), "guard": LoopDetector(), "system": system_with_memory(SYSTEM, prefs)}

    if "--resume" in sys.argv:
        run_id = sys.argv[sys.argv.index("--resume") + 1]
        state = run_with_checkpoints(backend, tools, store, resume_run_id=run_id, **common)
    else:
        question = " ".join(a for a in sys.argv[1:] if not a.startswith("--")) or "What changed in Kubernetes 1.36 and what should operators do?"
        state = run_with_checkpoints(backend, tools, store, state=AgentState(question), **common)
    print(f"run {state.run_id}: {state.stop_reason} after {state.steps} model calls, {state.tokens} tokens\n{state.answer}\nsources: {state.sources}")
    return 0 if state.stop_reason == "answered" else 2


if __name__ == "__main__":
    sys.exit(main())
