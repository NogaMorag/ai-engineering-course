"""Offline tests for the chapter 7 chat. Copy to ai-course/tests/test_ch07.py and run: uv run pytest -q"""

from __future__ import annotations

from ch07.chat import Conversation, Reply, Usage


class FakeBackend:
    """Records what it was asked and returns scripted replies, like a real backend would."""

    def __init__(self, replies: list[Reply]) -> None:
        self.replies = list(replies)
        self.calls: list[list[dict]] = []

    def send(self, steps: list[dict], system_instruction: str, max_output_tokens: int) -> Reply:
        self.calls.append(steps)
        return self.replies.pop(0)


def reply(text: str, input_tokens: int = 10, output_tokens: int = 5, status: str = "completed") -> Reply:
    return Reply(text=text, usage=Usage(input_tokens, output_tokens, 0), status=status)


def test_history_grows_and_alternates_roles() -> None:
    backend = FakeBackend([reply("Hi Noga."), reply("Your name is Noga.")])
    conversation = Conversation()
    conversation.ask(backend, "My name is Noga.")
    conversation.ask(backend, "What is my name?")
    second_call = backend.calls[1]
    assert [step["type"] for step in second_call] == ["user_input", "model_output", "user_input"]
    assert second_call[0]["content"][0]["text"] == "My name is Noga."
    assert second_call[1]["content"][0]["text"] == "Hi Noga."


def test_reset_clears_history_but_keeps_session_cost() -> None:
    backend = FakeBackend([reply("a", input_tokens=12), reply("b", input_tokens=30)])
    conversation = Conversation()
    conversation.ask(backend, "one")
    conversation.reset()
    assert conversation.turns == []
    conversation.ask(backend, "two")
    assert len(backend.calls[1]) == 1  # only the new message was sent
    assert conversation.session_usage.input_tokens == 42


def test_incomplete_status_is_marked_in_the_answer() -> None:
    backend = FakeBackend([reply("A long ans", status="incomplete")])
    conversation = Conversation()
    answer = conversation.ask(backend, "Explain everything.")
    assert "cut by the output limit" in answer


def test_cost_report_mentions_last_turn_and_session() -> None:
    backend = FakeBackend([reply("x", input_tokens=100, output_tokens=20)])
    conversation = Conversation()
    conversation.ask(backend, "hello")
    report = conversation.cost_report()
    assert "turns in history: 1" in report
    assert "input=   100" in report and "output=   20" in report
    assert "paid-tier estimate" in report
