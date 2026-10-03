"""Offline tests for the chapter 6 exercise (no network). Copy to ai-course/tests/test_ch06.py."""

import pytest

from ch06.generation_knobs import CLASSIFICATION_PROMPT, distinct_ratio, normalize


def test_normalize_ignores_case_whitespace_and_trailing_punctuation() -> None:
    assert normalize("  Negative. ") == "negative"
    assert normalize("NEGATIVE") == normalize("negative")


def test_distinct_ratio() -> None:
    assert distinct_ratio(["negative", "Negative.", "negative"]) == pytest.approx(1 / 3)
    assert distinct_ratio(["a", "b", "c"]) == pytest.approx(1.0)
    assert distinct_ratio([]) == 0.0


def test_classification_prompt_asks_for_one_word() -> None:
    assert "one word" in CLASSIFICATION_PROMPT
