"""Offline tests for chapter 28. Copy to ai-course/tests/test_ch28.py and run: uv run pytest -q"""

from __future__ import annotations

from collections import Counter

from ch28.mock import CATEGORIES, load_bank, main, sample


def test_bank_shape() -> None:
    bank = load_bank()
    assert len(bank) >= 40 and len({q.id for q in bank}) == len(bank)
    assert {q.category for q in bank} == set(CATEGORIES)
    assert all(len(q.answer) > 60 and q.question.endswith("?") or q.question.endswith(".") for q in bank)
    assert sum(1 for q in bank if q.tradeoff) >= 4


def test_sample_spreads_categories_and_is_reproducible() -> None:
    bank = load_bank()
    picked = sample(bank, 8, seed=3)
    assert len(picked) == 8 and len({q.id for q in picked}) == 8
    assert len(set(q.category for q in picked)) == 8  # one per category when n == number of categories
    assert [q.id for q in sample(bank, 8, seed=3)] == [q.id for q in picked]
    only = sample(bank, 5, categories=["rag", "evals"], seed=1)
    assert {q.category for q in only} <= {"rag", "evals"} and Counter(q.category for q in only).most_common(1)[0][1] <= 3
    assert len(sample(bank, 500, categories=["security"])) == sum(1 for q in bank if q.category == "security")


def test_cli_show_mode_runs_without_input(capsys) -> None:
    assert main(["--n", "3", "--seed", "1", "--show"]) == 0
    out = capsys.readouterr().out
    assert "model answer:" in out and "[3/3]" in out
