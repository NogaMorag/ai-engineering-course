"""Chapter 2 starter: the first call to a language model.

Copy this file to ai-course/ch02/hello_model.py and fill in the three TODOs.
Run from the course root (the folder that contains pyproject.toml):

    uv run --env-file .env python ch02/hello_model.py
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
    # TODO 1: prices are per one million tokens. Compute the cost of input_tokens plus
    # output_tokens and return it as a float in USD.
    raise NotImplementedError


def require_api_key() -> None:
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        sys.exit("No API key in the environment. Did you run with --env-file .env? See section 2.6.")


def main() -> None:
    require_api_key()
    model = os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite")
    prompt = "הסבירי בשני משפטים, בעברית, מה עושה מודל שפה."

    client = genai.Client()  # reads GEMINI_API_KEY / GOOGLE_API_KEY from the environment
    started = time.perf_counter()
    # TODO 2: call client.interactions.create with the model and the prompt as `input`,
    # and keep the returned interaction object. (No try/except here on purpose; see section 2.7.)
    interaction = ...
    elapsed = time.perf_counter() - started

    usage = interaction.usage
    # TODO 3: read the input, output and thought token counts from `usage`
    # (the object and each field may be None; treat None as 0).
    input_tokens = 0
    output_tokens = 0
    thought_tokens = 0

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
