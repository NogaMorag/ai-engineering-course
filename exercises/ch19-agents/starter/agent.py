"""Chapter 19 starter: a research agent as a loop you own.

    state   AgentState: the question, the explicit history, sources gathered, budgets, stop reason
    tools   a closed dict of Tool objects (same shape as chapter 10) dispatched safely
    loop    ask -> maybe tool calls -> dispatch all -> append results -> repeat, until an answer or a budget
    trace   one record per model call and per tool call

The model decides WHICH tool and WHEN; the code decides whether it may, how long, and how much.
"""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ValidationError

from ch09.schemas import clean_schema

StopReason = Literal["answered", "max_steps", "timeout", "token_budget", "loop_detected", "error"]


@dataclass
class Budgets:
    max_steps: int = 6  # model calls
    max_seconds: float = 90.0
    max_tokens: int = 40_000  # input + output, summed over the run


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    args_model: type[BaseModel]
    func: Callable[..., Any]
    side_effect: bool = False  # chapter 20 gates these behind approval and idempotency


@dataclass
class TraceRecord:
    step: int
    kind: Literal["model", "tool"]
    detail: dict[str, Any]
    elapsed_s: float


@dataclass
class AgentState:
    question: str
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    history: list[dict[str, Any]] = field(default_factory=list)  # explicit Interactions steps (chapter 7)
    sources: list[str] = field(default_factory=list)  # ids/urls of items actually read
    steps: int = 0
    tokens: int = 0
    seconds: float = 0.0
    status: Literal["running", "done"] = "running"
    stop_reason: StopReason | None = None
    answer: str = ""
    trace: list[TraceRecord] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, text: str) -> AgentState:
        data = json.loads(text)
        data["trace"] = [TraceRecord(**t) for t in data["trace"]]
        return cls(**data)


class ModelBackend(Protocol):
    """One call with explicit history and tool declarations; returns an interaction-like object."""

    def create(self, *, history: list[dict[str, Any]], tools: list[dict[str, Any]], system: str) -> Any: ...


SYSTEM = (
    "You are a research assistant. Use the tools to find and read sources, then answer the question in at "
    "most five sentences based only on what you read. Start by searching, read at most three items, and stop "
    "when you can answer. Mention which items you used by id."
)


def declarations(tools: dict[str, Tool]) -> list[dict[str, Any]]:
    return [
        {"type": "function", "name": t.name, "description": t.description, "parameters": clean_schema(t.args_model.model_json_schema())}
        for t in tools.values()
    ]


def dispatch(tools: dict[str, Tool], name: str, arguments: dict[str, Any]) -> tuple[str, bool]:
    tool = tools.get(name)
    if tool is None:
        return json.dumps({"error": f"unknown tool {name!r}"}), True
    try:
        args = tool.args_model.model_validate(arguments)
    except ValidationError as exc:
        return json.dumps({"error": "invalid arguments", "details": exc.errors(include_url=False)}, default=str), True
    try:
        result = tool.func(**args.model_dump())
    except Exception as exc:  # noqa: BLE001 - a failing tool becomes an error result the model can read
        return json.dumps({"error": f"{type(exc).__name__}: {exc}"}), True
    return json.dumps(result, ensure_ascii=False, default=str), False


def _usage_tokens(interaction: Any) -> int:
    usage = getattr(interaction, "usage", None)
    if not usage:
        return 0
    return (getattr(usage, "total_input_tokens", 0) or 0) + (getattr(usage, "total_output_tokens", 0) or 0)


def _model_output_step(text: str) -> dict[str, Any]:
    return {"type": "model_output", "content": [{"type": "text", "text": text}]}


def run_agent(
    backend: ModelBackend,
    tools: dict[str, Tool],
    state: AgentState,
    budgets: Budgets | None = None,
    *,
    clock: Callable[[], float] = time.monotonic,
    on_step: Callable[[AgentState], None] | None = None,
    guard: Callable[[AgentState, list[tuple[str, dict[str, Any]]]], StopReason | None] | None = None,
    system: str = SYSTEM,
) -> AgentState:
    """Drive the loop until the model answers or a budget stops it. `on_step` runs after every model call
    (chapter 20 persists the state there); `guard` may veto a round of tool calls (chapter 20's loop detector)."""
    budgets = budgets or Budgets()
    if not state.history:
        state.history.append({"type": "user_input", "content": [{"type": "text", "text": state.question}]})
    started = clock() - state.seconds  # resume keeps the clock running
    # TODO 2: the loop. Each iteration: stop with "max_steps" / "timeout" / "token_budget" when a budget is
    # spent; call backend.create(history=state.history, tools=declarations(tools), system=system) (an exception
    # -> trace record + _finish(state, "error")); count steps, tokens (_usage_tokens) and seconds; collect the
    # function_call steps; no calls -> store output_text as the answer, append a model_output step, on_step,
    # _finish "answered"; otherwise let `guard` veto the round, append one function_call step per call, dispatch
    # each call, append function_result steps (record sources via _collect_sources when not an error), add
    # trace records, update seconds, call on_step.
    raise NotImplementedError


def _collect_sources(state: AgentState, name: str, arguments: dict[str, Any]) -> None:
    source = arguments.get("item_id") or arguments.get("url")
    if name in ("read_item", "fetch_url") and source and source not in state.sources:
        state.sources.append(str(source))


def _finish(state: AgentState, reason: StopReason) -> AgentState:
    state.status = "done"
    state.stop_reason = reason
    if reason != "answered" and not state.answer:
        state.answer = f"Stopped before answering: {reason}."
    return state
