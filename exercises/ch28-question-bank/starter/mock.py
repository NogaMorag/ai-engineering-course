"""Chapter 28 starter: a randomized mock interview from the question bank.

    uv run python -m ch28.mock --n 12                       # 12 questions, mixed categories, answers hidden
    uv run python -m ch28.mock --n 6 --category rag evals   # only these categories
    uv run python -m ch28.mock --seed 7 --show               # reproducible set, answers shown

Press Enter after answering aloud to reveal the model answer. Score yourself 0 / 1 / 2 per question.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

BANK_PATH = Path(__file__).parent / "data" / "questions.jsonl"
CATEGORIES = ("fundamentals", "apis-prompting", "rag", "evals", "agents", "production", "security", "project")


@dataclass(frozen=True)
class Question:
    id: str
    category: str
    chapter: int
    question: str
    answer: str
    tradeoff: str = ""
    follow_up: str = ""


def load_bank(path: Path = BANK_PATH) -> list[Question]:
    return [Question(**json.loads(line)) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sample(bank: list[Question], n: int, *, categories: list[str] | None = None, seed: int | None = None) -> list[Question]:
    """Spread the picks across categories: round-robin over shuffled per-category lists."""
    # TODO: filter by categories; group by category; shuffle each group and the category order with
    # random.Random(seed); pick round-robin (one from each category in turn) until n or the pool is exhausted.
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Randomized mock interview from the question bank.")
    parser.add_argument("--n", type=int, default=10)
    parser.add_argument("--category", nargs="*", choices=CATEGORIES)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--show", action="store_true", help="print the answers immediately (for review)")
    args = parser.parse_args(argv)
    bank = load_bank()
    picked = sample(bank, args.n, categories=args.category, seed=args.seed)
    print(f"{len(picked)} questions from {len(bank)}; categories: {dict(Counter(q.category for q in picked))}\n")
    scores: list[int] = []
    for i, q in enumerate(picked, start=1):
        print(f"[{i}/{len(picked)}] ({q.category}, chapter {q.chapter})\n{q.question}\n")
        if not args.show:
            try:
                input("answer aloud, then press Enter ")
            except EOFError:
                pass
        print(f"model answer:\n{q.answer}")
        if q.tradeoff:
            print(f"tradeoff line: {q.tradeoff}")
        if not args.show:
            try:
                raw = input("your score (0 / 1 / 2): ").strip()
                scores.append(int(raw) if raw in {"0", "1", "2"} else 0)
            except EOFError:
                pass
        print("-" * 60)
    if scores:
        print(f"total: {sum(scores)}/{2 * len(scores)}; revisit chapters: {sorted({q.chapter for q, s in zip(picked, scores, strict=True) if s < 2})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
