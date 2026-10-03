"""Chapter 20 starter: guardrails for the loop. Loop detection, approval for side effects, idempotency."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, Field

from ch19.agent import AgentState, StopReason, Tool


def canonical(arguments: dict[str, Any]) -> str:
    return json.dumps(arguments, sort_keys=True, ensure_ascii=False, default=str)


class LoopDetector:
    """Veto a round that repeats a (tool, arguments) pair already executed in this run. Stateless: reads the history."""

    def __init__(self, max_repeats: int = 1) -> None:
        self.max_repeats = max_repeats

    def __call__(self, state: AgentState, proposed: list[tuple[str, dict[str, Any]]]) -> StopReason | None:
        # TODO 1: count (name, canonical(arguments)) pairs over the function_call steps in state.history;
        # if any proposed pair was already executed max_repeats times (or more) return "loop_detected"; else None.
        raise NotImplementedError


# ---------------------------------------------------------------- approval for side effects


class ApprovalDenied(Exception):
    pass


class ApprovalGate(Protocol):
    def approve(self, tool_name: str, arguments: dict[str, Any]) -> bool: ...


class ConsoleApproval:
    """Shows the EXACT action and waits for y/N. Anything but 'y' is a denial."""

    def approve(self, tool_name: str, arguments: dict[str, Any]) -> bool:
        print(f"\n=== approval needed: {tool_name} ===\n{json.dumps(arguments, ensure_ascii=False, indent=2)}")
        return input("run this? [y/N] ").strip().lower() == "y"


class ScriptedApproval:
    def __init__(self, decisions: list[bool]) -> None:
        self.decisions = list(decisions)
        self.asked: list[tuple[str, dict[str, Any]]] = []

    def approve(self, tool_name: str, arguments: dict[str, Any]) -> bool:
        self.asked.append((tool_name, arguments))
        return self.decisions.pop(0) if self.decisions else False


def gated(tool: Tool, gate: ApprovalGate) -> Tool:
    """A tool that asks before it acts. A denial becomes an error result the model can read, not a crash."""

    def func(**arguments: Any) -> Any:
        if not gate.approve(tool.name, arguments):
            raise ApprovalDenied(f"{tool.name} was not approved by the operator")
        return tool.func(**arguments)

    return Tool(tool.name, tool.description + " Requires operator approval.", tool.args_model, func, side_effect=True)


# ---------------------------------------------------------------- idempotency


class IdempotencyStore:
    def __init__(self, path: Path | str) -> None:
        self.conn = sqlite3.connect(str(path))
        self.conn.execute("CREATE TABLE IF NOT EXISTS idempotency (key TEXT PRIMARY KEY, tool TEXT NOT NULL, result TEXT NOT NULL, created_at REAL NOT NULL)")

    def get(self, key: str) -> Any | None:
        row = self.conn.execute("SELECT result FROM idempotency WHERE key = ?", (key,)).fetchone()
        return json.loads(row[0]) if row else None

    def put(self, key: str, tool: str, result: Any) -> None:
        self.conn.execute("INSERT OR REPLACE INTO idempotency (key, tool, result, created_at) VALUES (?, ?, ?, ?)", (key, tool, json.dumps(result, default=str), time.time()))
        self.conn.commit()


def default_key(tool_name: str, arguments: dict[str, Any]) -> str:
    explicit = arguments.get("idempotency_key")
    payload = explicit if explicit else canonical({k: v for k, v in arguments.items() if k != "idempotency_key"})
    return hashlib.sha256(f"{tool_name}\x00{payload}".encode()).hexdigest()[:32]


def idempotent(tool: Tool, store: IdempotencyStore, key_fn: Callable[[str, dict[str, Any]], str] = default_key) -> Tool:
    """Same key -> the stored result, and the side effect does not run again. A retry becomes safe."""

    def func(**arguments: Any) -> Any:
        # TODO 2: key = key_fn(tool.name, arguments); a stored result is returned with "replayed": True and the
        # side effect does NOT run; otherwise run tool.func(**arguments), store it under the key, return it.
        raise NotImplementedError

    return Tool(tool.name, tool.description, tool.args_model, func, side_effect=tool.side_effect)


# ---------------------------------------------------------------- the side-effecting tool for the exercise


class SendEmailArgs(BaseModel):
    to: str = Field(description="Recipient address.")
    subject: str
    body: str
    idempotency_key: str = Field(default="", description="Same key means the same message; a retry will not send twice.")


def make_send_email_tool(outbox: Path) -> Tool:
    """A stand-in for SMTP: every 'sent' message is a JSON file in the outbox directory."""
    outbox.mkdir(parents=True, exist_ok=True)

    def send_email(to: str, subject: str, body: str, idempotency_key: str = "") -> dict[str, Any]:
        message_id = hashlib.sha256(f"{to}|{subject}|{time.time_ns()}".encode()).hexdigest()[:12]
        (outbox / f"{message_id}.json").write_text(json.dumps({"to": to, "subject": subject, "body": body, "idempotency_key": idempotency_key}, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"status": "sent", "message_id": message_id, "to": to}

    return Tool("send_email", "Send an email to the user. Irreversible.", SendEmailArgs, send_email, side_effect=True)
