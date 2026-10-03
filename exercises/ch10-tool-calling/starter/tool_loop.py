"""Chapter 10 starter: the tool-calling loop, written by hand. Fill in the TODO in `run`.

Copy to ai-course/ch10/tool_loop.py. Run from the course root:

    uv run --env-file .env python -m ch10.tool_loop
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Protocol

from google import genai

from ch10.tools import dispatch, tool_declarations

SYSTEM = (
    "You are an assistant with two tools. Use search_notes for questions about the user's notes and "
    "fetch_url when the user gives a URL. Call a tool only when it is needed, use the tool results as "
    "your only source for facts about notes or pages, and answer briefly."
)


class ToolLoopExceeded(Exception):
    """The model kept asking for tools past the round limit."""


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]
    is_error: bool


@dataclass
class RunResult:
    text: str
    rounds: int
    tool_calls: list[ToolCall] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0


class ToolBackend(Protocol):
    """One request to the model. Returns an interaction-like object (id, status, steps, output_text, usage)."""

    def create(self, *, input: str | list[dict[str, Any]], previous_interaction_id: str | None = None) -> Any: ...


class GeminiToolBackend:
    def __init__(self, model: str, system_instruction: str = SYSTEM) -> None:
        self.model = model
        self.system_instruction = system_instruction
        self.client = genai.Client()

    def create(self, *, input: str | list[dict[str, Any]], previous_interaction_id: str | None = None) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "input": input,
            "system_instruction": self.system_instruction,
            "tools": tool_declarations(),
            "generation_config": {"temperature": 0.2, "max_output_tokens": 600},
        }
        if previous_interaction_id:
            kwargs["previous_interaction_id"] = previous_interaction_id
        return self.client.interactions.create(**kwargs)


def run(backend: ToolBackend, question: str, max_rounds: int = 5) -> RunResult:
    """Drive the loop: execute every proposed call, return all results together, stop when the model answers."""
    # TODO: interaction = backend.create(input=question); then for each round (1..max_rounds):
    #   - add interaction.usage tokens to the result (fields may be None)
    #   - collect steps whose .type == "function_call"; if none, return RunResult with output_text
    #   - for each call: dispatch(call.name, dict(call.arguments or {})) -> record a ToolCall and build
    #     {"type": "function_result", "call_id": call.id, "name": call.name, "result": output, "is_error": is_error}
    #   - interaction = backend.create(input=results, previous_interaction_id=interaction.id)
    # After the loop raise ToolLoopExceeded.
    raise NotImplementedError


def main() -> None:
    model = os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite")
    backend = GeminiToolBackend(model)
    for question in (
        "What do my notes say about temperature? Quote the file name.",
        "Fetch https://example.com and tell me the page title in one sentence.",
        "What is 17 times 23? Do not use any tool.",
    ):
        print(f"you>   {question}")
        outcome = run(backend, question)
        print(f"model> {outcome.text}")
        calls = ", ".join(f"{c.name}({'error' if c.is_error else 'ok'})" for c in outcome.tool_calls) or "none"
        print(f"       rounds={outcome.rounds} tools={calls} tokens in/out={outcome.input_tokens}/{outcome.output_tokens}\n")


if __name__ == "__main__":
    main()
