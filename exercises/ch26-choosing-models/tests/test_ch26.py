"""Offline tests for chapter 26. Copy to ai-course/tests/test_ch26.py and run: uv run pytest -q"""

from __future__ import annotations

from ch26.decision import (
    API_VS_OPEN_WEIGHTS,
    RULES,
    recommend,
    render_memo,
    render_table,
)


def test_recommendations_follow_the_observed_failure() -> None:
    assert recommend("the model does not know our private product facts").first.method.startswith("retrieval")
    assert recommend("the JSON fields are inconsistent and parsing fails").first.method.startswith("structured output")
    assert recommend("a narrow classification task hits an accuracy plateau").first.method.startswith("more and better labeled data")
    assert recommend("answers are good but too slow and expensive at p95").first.method.startswith("cheaper model")
    assert recommend("the next step depends on which link the tool finds").first.method.startswith("a bounded agent")
    assert recommend("I just want to use fine-tuning because it sounds cool") is not None  # matches the fine-tuning rule, which says data first
    assert recommend("completely unrelated words") is None


def test_table_and_memo_render() -> None:
    table = render_table()
    assert table.count("\n") >= len(RULES) + len(API_VS_OPEN_WEIGHTS) + 3 and "| observed failure |" in table and "| privacy |" in table
    memo = render_memo(title="t", symptom="s", evidence="e", decision="d", alternatives="a", cost="c", risks="r", how_we_will_know="h")
    assert memo.startswith("# Decision memo: t") and "**How we will know.** h" in memo
    assert all(rule.first.not_when and rule.then.why for rule in RULES)
