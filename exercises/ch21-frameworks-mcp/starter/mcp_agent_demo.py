"""Chapter 21 starter, day 41: the chapter 19 loop with a tool that lives in an MCP server.

    uv run --env-file .env python -m ch21.mcp_agent_demo "What do my notes say about temperature, and what did the feeds report about caching?"
"""

from __future__ import annotations

import sys
from pathlib import Path

from ch19.agent import AgentState, Budgets, run_agent
from ch19.gemini_backend import GeminiAgentBackend
from ch19.research_tools import make_tools
from ch21.mcp_client import as_agent_tools, course_notes_server


def main() -> int:
    question = " ".join(sys.argv[1:]) or "What do my notes say about temperature, and what did the feeds report about caching?"
    root = Path(__file__).resolve().parent.parent
    with course_notes_server(root) as toolbox:
        tools = make_tools() | as_agent_tools(toolbox, prefix="mcp_")
        state = run_agent(GeminiAgentBackend(), tools, AgentState(question), Budgets(max_steps=6))
    print(f"{state.stop_reason} after {state.steps} calls\n{state.answer}\n")
    for record in state.trace:
        if record.kind == "tool":
            print(f"  tool {record.detail['name']}  is_error={record.detail['is_error']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
