"""Chapter 6 solution: measure what temperature, max_output_tokens, thinking_level and seed do.

Run from the course root:

    uv run --env-file .env python -m ch06.generation_knobs

About 25 requests. On the free tier a short pause between calls keeps you under the per-minute
limit; if you still hit HTTP 429, wait a minute and run again.
"""

from __future__ import annotations

import os
import time

from google import genai

PAUSE_SECONDS = 1.0

CLASSIFICATION_PROMPT = (
    "Classify the sentiment of this support message as exactly one word, positive, negative or neutral: "
    "'The update broke my login again.'"
)
CREATIVE_PROMPT = "Write a six-word story about a lighthouse. Output only the story."
PUZZLE_PROMPT = (
    "A notebook and a pen cost 1.10 in total. The notebook costs 1.00 more than the pen. "
    "How much does the pen cost? Answer with the number only."
)


def normalize(text: str) -> str:
    return " ".join(text.lower().split()).strip(" .!\"'")


def distinct_ratio(outputs: list[str]) -> float:
    """Fraction of distinct answers among the outputs: 1.0 = all different, 1/n = all identical."""
    if not outputs:
        return 0.0
    return len({normalize(o) for o in outputs}) / len(outputs)


def generate(client: genai.Client, model: str, prompt: str, **config: object) -> genai.interactions.Interaction:
    interaction = client.interactions.create(model=model, input=prompt, generation_config=dict(config))
    time.sleep(PAUSE_SECONDS)
    return interaction


def temperature_sweep(client: genai.Client, model: str, runs: int = 3) -> None:
    print("== temperature sweep ==")
    for label, prompt in (("classification", CLASSIFICATION_PROMPT), ("creative", CREATIVE_PROMPT)):
        for temperature in (0.0, 0.7, 1.0):
            outputs = [
                (generate(client, model, prompt, temperature=temperature, max_output_tokens=60).output_text or "")
                for _ in range(runs)
            ]
            print(f"{label:<14} T={temperature:<4} distinct={distinct_ratio(outputs):.2f}  {[normalize(o)[:40] for o in outputs]}")
    print()


def truncation_demo(client: genai.Client, model: str) -> None:
    print("== truncation: max_output_tokens=20 ==")
    interaction = generate(client, model, "Explain in detail how a database index works.", max_output_tokens=20)
    usage = interaction.usage
    print(f"status={interaction.status}  output_tokens={(usage.total_output_tokens if usage else None)}")
    print(f"text: {(interaction.output_text or '').strip()!r}")
    print()


def thinking_demo(client: genai.Client, model: str) -> None:
    print("== thinking level on a small puzzle ==")
    for level in ("minimal", "high"):
        started = time.perf_counter()
        interaction = generate(client, model, PUZZLE_PROMPT, thinking_level=level, max_output_tokens=200)
        elapsed = time.perf_counter() - started - PAUSE_SECONDS
        usage = interaction.usage
        thought = (usage.total_thought_tokens if usage else None) or 0
        print(f"thinking_level={level:<8} answer={normalize(interaction.output_text or '')!r:<8} thought_tokens={thought:<5} latency={elapsed:.2f}s")
    print()


def seed_demo(client: genai.Client, model: str) -> None:
    print("== same seed twice at temperature 1.0 ==")
    outputs = [
        (generate(client, model, CREATIVE_PROMPT, temperature=1.0, seed=7, max_output_tokens=60).output_text or "")
        for _ in range(2)
    ]
    print(f"identical={normalize(outputs[0]) == normalize(outputs[1])}  {[normalize(o) for o in outputs]}")
    print("A seed makes repeats *likely* identical, not guaranteed: servers and hardware change.")


def main() -> None:
    model = os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite")
    client = genai.Client()
    print(f"model: {model}\n")
    temperature_sweep(client, model)
    truncation_demo(client, model)
    thinking_demo(client, model)
    seed_demo(client, model)


if __name__ == "__main__":
    main()
