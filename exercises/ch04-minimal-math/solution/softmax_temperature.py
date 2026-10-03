"""Chapter 4 solution: softmax, temperature, and the loss a language model is trained on.

Run from the course root:

    uv run python -m ch04.softmax_temperature
"""

from __future__ import annotations

import numpy as np


def softmax(logits: list[float] | np.ndarray, temperature: float = 1.0) -> np.ndarray:
    """Turn raw scores into probabilities that sum to 1. Lower temperature = sharper."""
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    z = np.asarray(logits, dtype=float) / temperature
    z = z - z.max()  # subtracting the maximum keeps exp() from overflowing; result is unchanged
    weights = np.exp(z)
    return weights / weights.sum()


def negative_log_likelihood(probability_of_correct: float) -> float:
    """The loss for one example: large when the model gave the right answer a small probability."""
    if not 0 < probability_of_correct <= 1:
        raise ValueError("probability must be in (0, 1]")
    return float(-np.log(probability_of_correct))


def main() -> None:
    logits = [2.0, 1.0, 0.0]
    print(f"logits: {logits}")
    for temperature in (0.5, 1.0, 2.0):
        probs = softmax(logits, temperature)
        print(f"  T={temperature:<4} probabilities={np.round(probs, 3).tolist()}  sum={probs.sum():.3f}")

    print()
    print("loss for one example (negative log of the probability given to the correct answer):")
    for p in (0.9, 0.8, 0.5, 0.2, 0.05):
        print(f"  p(correct)={p:<5} loss={negative_log_likelihood(p):.3f}")


if __name__ == "__main__":
    main()
