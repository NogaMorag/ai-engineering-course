"""Chapter 5 starter: where does the model's information live? Three probes.

Copy to ai-course/ch05/knowledge_probe.py and fill in the TODO. Run from the course root:

    uv run --env-file .env python -m ch05.knowledge_probe
"""

from __future__ import annotations

import os

from google import genai

# A made-up fact that cannot be in any training data.
PRIVATE_FACT = "The internal backup rotation code name at Example Corp is TULIP-7."

QUESTION = "What is the internal backup rotation code name at Example Corp? Answer in one short sentence."
NEWS_PROMPT = (
    "What was the most important technology news yesterday? Answer in one sentence, "
    "then say which date you believe today is and how confident you are."
)


def build_probes(private_fact: str) -> list[tuple[str, str]]:
    """Return (label, prompt) pairs. Kept as a function so the structure can be tested offline."""
    with_context = f"Use only the note below to answer.\n\nNote: {private_fact}\n\nQuestion: {QUESTION}"
    return [
        ("after the cutoff", NEWS_PROMPT),
        ("private fact, without context", QUESTION),
        ("private fact, with context", with_context),
    ]


def ask(client: genai.Client, model: str, prompt: str) -> str:
    # TODO: call client.interactions.create with the model, the prompt as input, and
    # generation_config={"temperature": 0.0, "max_output_tokens": 200}; return the stripped output_text
    # (output_text may be None: treat it as an empty string).
    raise NotImplementedError


def main() -> None:
    model = os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite")
    client = genai.Client()
    for label, prompt in build_probes(PRIVATE_FACT):
        print(f"== {label} ==")
        print(ask(client, model, prompt))
        print()
    print("Expected pattern: probe 1 cannot know yesterday's news (weights have a cutoff);")
    print("probe 2 should admit it does not know (or invent something: note it if it does);")
    print("probe 3 answers TULIP-7, because the fact is in the context of this request only.")


if __name__ == "__main__":
    main()
