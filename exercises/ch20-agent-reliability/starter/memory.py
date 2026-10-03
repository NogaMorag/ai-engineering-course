"""Chapter 20 starter: three kinds of memory, kept apart.

    conversation state   the explicit history inside AgentState (this run only)
    task state           AgentState itself: budgets, sources, stop reason (this run only, resumable)
    long-term memory     UserPreferences: survives runs, is small, is read at start and written on purpose
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ch11.llm_client import LLMClient


@dataclass
class UserPreferences:
    name: str = ""
    language: str = "he"  # "he" or "en"
    skip_topics: list[str] = field(default_factory=list)
    max_sentences: int = 5


class UserMemory:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def load(self) -> UserPreferences:
        if not self.path.exists():
            return UserPreferences()
        return UserPreferences(**json.loads(self.path.read_text(encoding="utf-8")))

    def save(self, prefs: UserPreferences) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(prefs), ensure_ascii=False, indent=2), encoding="utf-8")


def system_with_memory(base_system: str, prefs: UserPreferences) -> str:
    """Memory changes behaviour only through the prompt, visibly, in one place."""
    language = "Hebrew" if prefs.language == "he" else "English"
    lines = [base_system, f"Answer in {language}, in at most {prefs.max_sentences} sentences."]
    if prefs.name:
        lines.append(f"The user's name is {prefs.name}.")
    if prefs.skip_topics:
        lines.append("The user is not interested in: " + ", ".join(prefs.skip_topics) + ". Do not spend tool calls on those topics.")
    return "\n".join(lines)


SUMMARY_SYSTEM = "Compress the earlier research steps into a short factual summary: which searches were made, which items were read, and what they said. Keep ids. No opinions."


def summarize_history(client: LLMClient, history: list[dict[str, Any]], keep_last: int = 4) -> list[dict[str, Any]]:
    """Replace everything but the first user turn and the last `keep_last` steps with one model-written summary.

    Cheaper context, at a price: details not in the summary are gone for the rest of the run.
    """
    if len(history) <= keep_last + 1:
        return history
    head, middle, tail = history[0], history[1:-keep_last], history[-keep_last:]
    completion = client.complete(json.dumps(middle, ensure_ascii=False)[:20_000], system=SUMMARY_SYSTEM, max_output_tokens=400, temperature=0.0)
    summary = {"type": "user_input", "content": [{"type": "text", "text": f"Summary of earlier research steps:\n{completion.text.strip()}"}]}
    return [head, summary, *tail]
