"""Chapter 20 starter: checkpoint the agent state after every step, and resume a run by id after a crash."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any

from ch19.agent import AgentState, Budgets, ModelBackend, Tool, run_agent


class RunStore:
    def __init__(self, path: Path | str) -> None:
        self.conn = sqlite3.connect(str(path))
        self.conn.execute("CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, status TEXT NOT NULL, steps INTEGER NOT NULL, updated_at REAL NOT NULL, state TEXT NOT NULL)")

    def save(self, state: AgentState) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO runs (run_id, status, steps, updated_at, state) VALUES (?, ?, ?, ?, ?)",
            (state.run_id, state.status, state.steps, time.time(), state.to_json()),
        )
        self.conn.commit()

    def load(self, run_id: str) -> AgentState | None:
        row = self.conn.execute("SELECT state FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        return AgentState.from_json(row[0]) if row else None

    def list_runs(self) -> list[dict[str, Any]]:
        rows = self.conn.execute("SELECT run_id, status, steps, updated_at FROM runs ORDER BY updated_at DESC").fetchall()
        return [{"run_id": r[0], "status": r[1], "steps": r[2], "updated_at": r[3]} for r in rows]


def run_with_checkpoints(
    backend: ModelBackend,
    tools: dict[str, Tool],
    store: RunStore,
    *,
    state: AgentState | None = None,
    resume_run_id: str | None = None,
    budgets: Budgets | None = None,
    **kwargs: Any,
) -> AgentState:
    """Start a new run or continue a saved one. The state is saved after every completed round and at the end."""
    budgets = budgets or Budgets()
    # TODO 3: with resume_run_id load the state (KeyError when missing; return it as is when status == "done");
    # otherwise require `state`. Save once before starting, run run_agent(..., on_step=store.save, **kwargs),
    # save the final state and return it.
    raise NotImplementedError
