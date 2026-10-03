"""Smoke tests for the course workbench. No network, no API key needed.

Copy to ai-course/tests/test_smoke.py and run:  uv run pytest -q
"""

import sys

import pytest

from ch02.hello_model import estimate_paid_cost


def test_python_version_is_3_12() -> None:
    assert sys.version_info[:2] == (3, 12)


def test_sdk_is_installed() -> None:
    import google.genai  # noqa: F401  (import succeeding is the test)


def test_paid_cost_estimate() -> None:
    # 1M input tokens at $0.30 plus 1M output tokens at $2.50 = $2.80
    assert estimate_paid_cost(1_000_000, 1_000_000, 0.30, 2.50) == pytest.approx(2.80)
    assert estimate_paid_cost(0, 0) == 0.0
