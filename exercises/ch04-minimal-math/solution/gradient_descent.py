"""Chapter 4 solution: gradient descent on one parameter, including what a bad learning rate does.

Run from the course root:

    uv run python -m ch04.gradient_descent
"""

from __future__ import annotations

from collections.abc import Iterator

TARGET = 3.0


def loss(w: float) -> float:
    """How wrong the parameter is. Zero exactly at the target."""
    return (w - TARGET) ** 2


def gradient(w: float) -> float:
    """Derivative of the loss: the direction in which the loss grows fastest."""
    return 2 * (w - TARGET)


def descend(w: float, learning_rate: float, steps: int) -> Iterator[tuple[int, float, float]]:
    """Yield (step, w, loss) while moving against the gradient."""
    yield 0, w, loss(w)
    for step in range(1, steps + 1):
        w = w - learning_rate * gradient(w)
        yield step, w, loss(w)


def main() -> None:
    print("learning rate 0.1: steady descent toward w = 3")
    for step, w, value in descend(0.0, learning_rate=0.1, steps=10):
        print(f"  step {step:<2} w={w:7.4f}  loss={value:8.4f}")

    print()
    print("learning rate 1.1: each step overshoots and the loss grows")
    for step, w, value in descend(0.0, learning_rate=1.1, steps=5):
        print(f"  step {step:<2} w={w:9.4f}  loss={value:11.4f}")


if __name__ == "__main__":
    main()
