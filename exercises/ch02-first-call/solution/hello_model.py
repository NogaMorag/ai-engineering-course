"""Chapter 2 solution: the first call to a language model.

Run from the course root (the folder that contains pyproject.toml):

    uv run --env-file .env python ch02/hello_model.py

Prints the model's answer, the token usage reported by the API, the latency,
and what the call would have cost on the paid tier.
"""

from __future__ import annotations

import os
import sys
import time

from google import genai

# Paid-tier list prices per 1M tokens for the default fast model (checked 2026-10-03).
# On the free tier the real cost is 0; this is for building intuition only.
DEFAULT_PRICE_INPUT = 0.30
DEFAULT_PRICE_OUTPUT = 2.50


def estimate_paid_cost(
    input_tokens: int,
    output_tokens: int,
    price_input: float = DEFAULT_PRICE_INPUT,
    price_output: float = DEFAULT_PRICE_OUTPUT,
) -> float:
    """Return the price in USD for the given token counts at the given per-1M rates."""
    return (input_tokens * price_input + output_tokens * price_output) / 1_000_000


def require_api_key() -> None:
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        sys.exit("No API key in the environment. Did you run with --env-file .env? See section 2.6.")


def main() -> None:
    require_api_key()
    model = os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite")
    prompt = "הסבירי בשני משפטים, בעברית, מה עושה מודל שפה."

    client = genai.Client()  # reads GEMINI_API_KEY / GOOGLE_API_KEY from the environment
    started = time.perf_counter()
    # No try/except on purpose: if the key, the model name or the rate limit is wrong,
    # the traceback's last line says exactly what happened. Chapter 11 adds real error handling.
    interaction = client.interactions.create(model=model, input=prompt)
    elapsed = time.perf_counter() - started

    usage = interaction.usage
    input_tokens = (usage.total_input_tokens if usage else None) or 0
    output_tokens = (usage.total_output_tokens if usage else None) or 0
    thought_tokens = (usage.total_thought_tokens if usage else None) or 0

    print(interaction.output_text)
    print("-" * 40)
    print(f"model:           {model}")
    print(f"input tokens:    {input_tokens}")
    print(f"output tokens:   {output_tokens}")
    print(f"thought tokens:  {thought_tokens}")
    print(f"latency:         {elapsed:.2f} s")
    print(f"paid-tier price: ${estimate_paid_cost(input_tokens, output_tokens):.6f} (free tier: $0)")


if __name__ == "__main__":
    main()
