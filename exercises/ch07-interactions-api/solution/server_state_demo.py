"""Chapter 7 solution: the other way to hold a conversation, with state kept by the provider.

Run from the course root:

    uv run --env-file .env python -m ch07.server_state_demo

Two requests. The second sends only the new message plus the id of the first interaction;
the provider supplies the history. Compare the input token counts with the explicit-history chat.
"""

from __future__ import annotations

import os

from google import genai

SYSTEM = "You are a concise assistant. Answer in one short sentence."


def main() -> None:
    model = os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite")
    client = genai.Client()

    first = client.interactions.create(
        model=model,
        input="My name is Noga and I am learning AI engineering.",
        system_instruction=SYSTEM,
    )
    print("first :", (first.output_text or "").strip())
    print("        input tokens:", first.usage.total_input_tokens if first.usage else None)

    second = client.interactions.create(
        model=model,
        input="What is my name and what am I learning?",
        system_instruction=SYSTEM,  # request-scoped: must be sent again
        previous_interaction_id=first.id,
    )
    print("second:", (second.output_text or "").strip())
    print("        input tokens:", second.usage.total_input_tokens if second.usage else None)
    print()
    print("The provider stored the first interaction (store=True by default) and used it as context.")
    print("Pass store=False when you do not want an interaction kept for continuation.")


if __name__ == "__main__":
    main()
