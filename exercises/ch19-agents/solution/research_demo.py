"""Chapter 19 solution, day 37: run the research agent on a topical question within budgets.

    uv run --env-file .env python -m ch19.research_demo "What is slowing down Rust developers and what helps?"
"""

from __future__ import annotations

import json
import sys

from ch19.agent import AgentState, Budgets, run_agent
from ch19.gemini_backend import GeminiAgentBackend
from ch19.research_tools import make_tools


def main() -> int:
    question = " ".join(sys.argv[1:]) or "What is slowing down Rust developers and what helps?"
    state = run_agent(GeminiAgentBackend(), make_tools(), AgentState(question), Budgets(max_steps=6, max_seconds=90, max_tokens=40_000))
    print(f"answer ({state.stop_reason}, {state.steps} model calls, {state.tokens} tokens, {state.seconds:.1f}s):\n{state.answer}\n")
    print("sources read:", ", ".join(state.sources) or "none")
    print("\ntrace:")
    for record in state.trace:
        print(f"  step {record.step} {record.kind:<5} {record.elapsed_s:>6.2f}s  {json.dumps(record.detail, ensure_ascii=False)[:110]}")
    print(f"\nrun id {state.run_id}; state is {len(state.to_json()):,} bytes of JSON")
    return 0 if state.stop_reason == "answered" else 2


if __name__ == "__main__":
    sys.exit(main())
