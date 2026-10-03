"""Chapter 3 starter: classification metrics from a confusion matrix, plus a threshold sweep.

Copy to ai-course/ch03/metrics.py and fill in the TODOs. Run from the course root:

    uv run python -m ch03.metrics
"""

from __future__ import annotations

from dataclasses import dataclass

from ch03.toy_classifier import MESSAGES, score, split, train


@dataclass(frozen=True)
class Confusion:
    """The four cells of a binary confusion matrix. 'Positive' means 'predicted urgent'."""

    tp: int  # urgent, predicted urgent
    fp: int  # not urgent, predicted urgent (false alarm)
    fn: int  # urgent, predicted not urgent (missed)
    tn: int  # not urgent, predicted not urgent

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.fn + self.tn

    def accuracy(self) -> float:
        # TODO 1: correct decisions divided by all decisions; 0.0 when there are no decisions.
        raise NotImplementedError

    def precision(self) -> float:
        # TODO 2: of everything predicted positive, the fraction that really is positive.
        # Return 0.0 instead of dividing by zero.
        raise NotImplementedError

    def recall(self) -> float:
        # TODO 3: of everything really positive, the fraction we caught. 0.0 instead of dividing by zero.
        raise NotImplementedError

    def f1(self) -> float:
        # TODO 4: harmonic mean of precision and recall: 2*P*R / (P + R); 0.0 when both are 0.
        raise NotImplementedError


def confusion(predictions: list[bool], truths: list[bool]) -> Confusion:
    # TODO 5: raise ValueError if the lists differ in length, then count the four cells.
    raise NotImplementedError


def report(name: str, c: Confusion) -> None:
    print(
        f"{name:<24} TP={c.tp:<3} FP={c.fp:<3} FN={c.fn:<3} TN={c.tn:<3} "
        f"acc={c.accuracy():.2f}  precision={c.precision():.2f}  recall={c.recall():.2f}  f1={c.f1():.2f}"
    )


def main() -> None:
    # The worked example from the chapter: 100 tickets, 8 truly urgent, the model flags 10.
    report("chapter example", Confusion(tp=6, fp=4, fn=2, tn=88))
    report("baseline: never urgent", Confusion(tp=0, fp=0, fn=8, tn=92))
    print()

    train_set, held_out = split(MESSAGES)
    weights = train(train_set)
    truths = [urgent for _, urgent in held_out]
    scores = [score(weights, text) for text, _ in held_out]
    print("held-out scores (positive should mean urgent):")
    for (text, urgent), s in zip(held_out, scores):
        print(f"  {s:+.2f}  {'URGENT ' if urgent else 'routine'}  {text}")
    print()
    print("threshold sweep (higher threshold = stricter about calling something urgent):")
    for threshold in (-0.10, -0.05, 0.00, 0.10, 0.15):
        predictions = [s > threshold for s in scores]
        report(f"threshold {threshold:+.2f}", confusion(predictions, truths))
    print()
    print("Ten examples are far too few to trust any of these decimals; the shape of the")
    print("trade-off (precision up, recall down as the threshold rises) is the lesson.")


if __name__ == "__main__":
    main()
