"""Offline tests for chapter 21 (no API key; the MCP test starts a local subprocess). Copy to ai-course/tests/test_ch21.py."""

from __future__ import annotations

import json
import re
from pathlib import Path

from ch19.agent import dispatch
from ch21.graph_agent import (
    build_graph,
    config_for,
    deliver_to_outbox,
    open_checkpointer,
    resume_run,
    start_run,
)
from ch21.mcp_client import as_agent_tools, course_notes_server

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def fake_research(question: str) -> tuple[str, list[str]]:
    return f"Draft answer to: {question}", ["f03", "f17"]


def test_graph_pauses_at_review_and_resumes_by_thread_id(tmp_path: Path) -> None:
    delivered: list[tuple[str, list[str]]] = []

    def deliver(draft: str, sources: list[str]) -> str:
        delivered.append((draft, sources))
        return "receipt-1"

    db = tmp_path / "graph.sqlite"
    app = build_graph(fake_research, deliver, open_checkpointer(db))
    payload = start_run(app, "what changed in kubernetes 1.36?", "thread-a")
    assert payload["draft"].startswith("Draft answer") and payload["sources"] == ["f03", "f17"]
    assert app.get_state(config_for("thread-a")).next == ("review",) and delivered == []

    # a NEW graph instance over the same checkpoint database continues the same thread
    app2 = build_graph(fake_research, deliver, open_checkpointer(db))
    final = resume_run(app2, "thread-a", approved=True)
    assert final["delivered"] == "receipt-1" and final["approved"] is True and len(delivered) == 1
    assert app2.get_state(config_for("thread-a")).next == ()

    start_run(app2, "another question", "thread-b")
    rejected = resume_run(app2, "thread-b", approved=False)
    assert rejected["delivered"] == "discarded" and len(delivered) == 1


def test_deliver_to_outbox_writes_a_file(tmp_path: Path) -> None:
    receipt = deliver_to_outbox(tmp_path / "outbox")("the brief", ["f01"])
    text = Path(receipt).read_text(encoding="utf-8")
    assert text.startswith("the brief") and "Sources: f01" in text


def test_mcp_server_tools_are_listed_called_and_bridged_into_the_loop() -> None:
    with course_notes_server(PROJECT_ROOT) as toolbox:
        names = {t.name for t in toolbox.tools}
        assert {"search_notes", "today"} <= names
        declarations = {d["name"]: d for d in toolbox.declarations()}
        assert declarations["search_notes"]["type"] == "function" and "query" in declarations["search_notes"]["parameters"]["properties"]
        assert '"title"' not in json.dumps(declarations["search_notes"]["parameters"])

        text, is_error = toolbox.call("today", {})
        assert not is_error and re.fullmatch(r"\d{4}-\d{2}-\d{2}", text.strip())
        text, is_error = toolbox.call("search_notes", {"query": "temperature"})
        assert not is_error and json.loads(text)["matches"]
        text, is_error = toolbox.call("search_notes", {"nope": 1})
        assert is_error

        tools = as_agent_tools(toolbox, prefix="mcp_")
        assert set(tools) >= {"mcp_search_notes", "mcp_today"}
        out, err = dispatch(tools, "mcp_search_notes", {"query": "temperature", "max_results": 2})
        assert not err and len(json.loads(out)["matches"]) <= 2
        out, err = dispatch(tools, "mcp_search_notes", {"nope": 1})
        assert err and "RuntimeError" in out
