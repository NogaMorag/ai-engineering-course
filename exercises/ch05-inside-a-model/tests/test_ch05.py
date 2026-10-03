"""Offline tests for the chapter 5 exercise (no network). Copy to ai-course/tests/test_ch05.py."""

import pytest

from ch05.knowledge_probe import PRIVATE_FACT, build_probes
from ch05.token_counting import TEXTS, chars_per_token, format_row


def test_texts_cover_six_formats_and_are_non_empty() -> None:
    assert len(TEXTS) == 6
    assert all(text.strip() for text in TEXTS.values())
    assert any("א" <= ch <= "ת" for ch in TEXTS["hebrew paragraph"])  # contains Hebrew letters


def test_chars_per_token() -> None:
    assert chars_per_token(400, 100) == pytest.approx(4.0)
    assert chars_per_token(10, 0) == 0.0


def test_format_row_contains_the_numbers() -> None:
    row = format_row("x", 400, 100)
    assert "chars= 400" in row and "tokens= 100" in row and "chars/token= 4.00" in row


def test_probes_structure() -> None:
    probes = build_probes(PRIVATE_FACT)
    labels = [label for label, _ in probes]
    assert labels == ["after the cutoff", "private fact, without context", "private fact, with context"]
    without, with_ctx = probes[1][1], probes[2][1]
    assert "TULIP-7" not in without
    assert "TULIP-7" in with_ctx
