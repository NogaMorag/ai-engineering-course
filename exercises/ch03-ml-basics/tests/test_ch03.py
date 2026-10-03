"""Tests for the chapter 3 exercise. Copy to ai-course/tests/test_ch03.py and run: uv run pytest -q"""

import pytest

from ch03.metrics import Confusion, confusion
from ch03.toy_classifier import MESSAGES, accuracy, split, tokenize, train, with_leak


def test_chapter_example_metrics() -> None:
    c = Confusion(tp=6, fp=4, fn=2, tn=88)
    assert c.accuracy() == pytest.approx(0.94)
    assert c.precision() == pytest.approx(0.6)
    assert c.recall() == pytest.approx(0.75)
    assert c.f1() == pytest.approx(0.6667, abs=1e-3)


def test_zero_division_yields_zero_not_a_crash() -> None:
    c = Confusion(tp=0, fp=0, fn=0, tn=5)
    assert c.precision() == 0.0
    assert c.recall() == 0.0
    assert c.f1() == 0.0


def test_confusion_counts_each_cell() -> None:
    c = confusion([True, True, False, False], [True, False, True, False])
    assert (c.tp, c.fp, c.fn, c.tn) == (1, 1, 1, 1)


def test_confusion_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError):
        confusion([True], [True, False])


def test_tokenize_lowercases_drops_punctuation_and_stop_words() -> None:
    assert tokenize("The Site is DOWN!") == ["site", "down"]
    assert tokenize("API returns 500 errors") == ["api", "returns", "500", "errors"]


def test_split_is_deterministic_and_disjoint() -> None:
    train_a, held_a = split(MESSAGES)
    train_b, held_b = split(MESSAGES)
    assert train_a == train_b and held_a == held_b
    assert len(train_a) == 30 and len(held_a) == 10
    assert not (set(train_a) & set(held_a))


def test_model_memorizes_training_data_and_generalizes_only_partly() -> None:
    train_set, held_out = split(MESSAGES)
    weights = train(train_set)
    assert accuracy(weights, train_set) == 1.0  # memorized: 30 messages, hundreds of possible words
    assert 0.5 < accuracy(weights, held_out) < 1.0  # better than chance, far from perfect


def test_leak_makes_the_model_look_perfect() -> None:
    train_set, held_out = split(MESSAGES)
    leaked = train(with_leak(train_set))
    assert accuracy(leaked, with_leak(held_out)) == 1.0
