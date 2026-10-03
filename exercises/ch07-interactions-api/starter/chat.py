"""Chapter 7 starter: a command-line chat that keeps the conversation history itself.

Copy to ai-course/ch07/chat.py (with an empty ch07/__init__.py) and fill in the three TODOs.
Run from the course root:

    uv run --env-file .env python -m ch07.chat

Commands inside the chat: /cost  /history  /reset  /quit
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Protocol

from google import genai

from ch02.hello_model import estimate_paid_cost

SYSTEM_INSTRUCTION = (
    "You are a concise assistant for a software developer who is learning AI engineering. "
    "Answer in the language of the question. Keep answers under 120 words unless asked otherwise."
)


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    thought_tokens: int = 0

    def add(self, other: Usage) -> None:
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.thought_tokens += other.thought_tokens


@dataclass
class Reply:
    text: str
    usage: Usage
    status: str


class ChatBackend(Protocol):
    """Anything that can answer a conversation. The real one calls Gemini; tests use a fake."""

    def send(self, steps: list[dict], system_instruction: str, max_output_tokens: int) -> Reply: ...


class GeminiBackend:
    def __init__(self, model: str) -> None:
        self.model = model
        self.client = genai.Client()

    def send(self, steps: list[dict], system_instruction: str, max_output_tokens: int) -> Reply:
        # TODO 1: call client.interactions.create with model, input=steps, system_instruction and
        # generation_config={"temperature": 0.3, "max_output_tokens": max_output_tokens}.
        # Build a Usage from interaction.usage (fields may be None -> 0) and return
        # Reply(text=output_text stripped, usage=..., status=str(interaction.status)).
        raise NotImplementedError


@dataclass
class Turn:
    role: str  # "user" or "model"
    text: str


@dataclass
class Conversation:
    system_instruction: str = SYSTEM_INSTRUCTION
    turns: list[Turn] = field(default_factory=list)
    per_turn_usage: list[Usage] = field(default_factory=list)
    session_usage: Usage = field(default_factory=Usage)

    def to_steps(self) -> list[dict]:
        """The whole history as Interactions steps: user_input and model_output, alternating."""
        # TODO 2: for each turn build {"type": "user_input" | "model_output",
        #                              "content": [{"type": "text", "text": turn.text}]}
        raise NotImplementedError

    def ask(self, backend: ChatBackend, text: str, max_output_tokens: int = 400) -> str:
        self.turns.append(Turn("user", text))
        reply = backend.send(self.to_steps(), self.system_instruction, max_output_tokens)
        answer = reply.text
        if reply.status == "incomplete":
            answer += "\n[the reply was cut by the output limit]"
        self.turns.append(Turn("model", answer))
        self.per_turn_usage.append(reply.usage)
        self.session_usage.add(reply.usage)
        return answer

    def reset(self) -> None:
        """Forget the history (the session cost total is kept on purpose)."""
        self.turns.clear()
        self.per_turn_usage.clear()

    def cost_report(self) -> str:
        # TODO 3: report turns in history, the last turn's tokens, the session totals, and the
        # paid-tier estimate (estimate_paid_cost(input, output + thought)).
        raise NotImplementedError


def main() -> None:
    model = os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite")
    backend = GeminiBackend(model)
    conversation = Conversation()
    print(f"chat with {model}. Commands: /cost /history /reset /quit")
    while True:
        try:
            text = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text == "/quit":
            break
        if text == "/reset":
            conversation.reset()
            print("history cleared")
            continue
        if text == "/cost":
            print(conversation.cost_report())
            continue
        if text == "/history":
            for turn in conversation.turns:
                print(f"  {turn.role:<5} {turn.text[:80]}")
            continue
        answer = conversation.ask(backend, text)
        last = conversation.per_turn_usage[-1]
        print(f"model> {answer}")
        print(f"       [input {last.input_tokens} | output {last.output_tokens} tokens]")


if __name__ == "__main__":
    main()
