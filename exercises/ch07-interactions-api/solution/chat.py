"""Chapter 7 solution: a command-line chat that keeps the conversation history itself.

Run from the course root:

    uv run --env-file .env python -m ch07.chat

Commands inside the chat: /cost  /history  /reset  /quit
Every turn re-sends the whole history, so input tokens grow turn by turn: watch /cost.
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
        interaction = self.client.interactions.create(
            model=self.model,
            input=steps,
            system_instruction=system_instruction,
            generation_config={"temperature": 0.3, "max_output_tokens": max_output_tokens},
        )
        u = interaction.usage
        usage = Usage(
            input_tokens=(u.total_input_tokens if u else None) or 0,
            output_tokens=(u.total_output_tokens if u else None) or 0,
            thought_tokens=(u.total_thought_tokens if u else None) or 0,
        )
        return Reply(text=(interaction.output_text or "").strip(), usage=usage, status=str(interaction.status or "unknown"))


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
        return [
            {
                "type": "user_input" if turn.role == "user" else "model_output",
                "content": [{"type": "text", "text": turn.text}],
            }
            for turn in self.turns
        ]

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
        last = self.per_turn_usage[-1] if self.per_turn_usage else Usage()
        total = self.session_usage
        return (
            f"turns in history: {len(self.turns) // 2}\n"
            f"last turn:   input={last.input_tokens:>6}  output={last.output_tokens:>5}  thought={last.thought_tokens:>4}\n"
            f"session:     input={total.input_tokens:>6}  output={total.output_tokens:>5}  thought={total.thought_tokens:>4}\n"
            f"paid-tier estimate for the session: ${estimate_paid_cost(total.input_tokens, total.output_tokens + total.thought_tokens):.6f}"
        )


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
