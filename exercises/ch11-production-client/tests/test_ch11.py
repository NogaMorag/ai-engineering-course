"""Offline tests for chapter 11. Copy to ai-course/tests/test_ch11.py and run: uv run pytest -q"""

from __future__ import annotations

import json
import random

import pytest

from ch11.llm_client import (
    Completion,
    FakeClient,
    LLMBadRequest,
    LLMError,
    LLMRateLimited,
    LLMUnavailable,
    RetryPolicy,
    classify,
    with_retries,
)


def cli():
    """Imported lazily: ch11/summarize_url.py is written on day 19, and the client tests must collect without it."""
    from ch11 import summarize_url

    return summarize_url


VALID = {
    "is_article": True,
    "headline": "Cargo-Lite 2.0 adds a shared build cache",
    "bullets": ["Version 2.0 was released.", "Builds dropped from 41 to 6 minutes.", "The old config format goes away in 3.0."],
    "why_it_matters": "Why it matters: faster builds for Rust teams.",
    "tags": ["rust"],
    "confidence": "high",
}
NOT_ARTICLE = {"is_article": False, "headline": "", "bullets": [], "why_it_matters": "", "tags": [], "confidence": "low"}


class FakeSdkError(Exception):
    def __init__(self, status_code: int | None, message: str = "boom") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def test_classify_by_status_code() -> None:
    assert isinstance(classify(FakeSdkError(429)), LLMRateLimited)
    assert isinstance(classify(FakeSdkError(503)), LLMUnavailable)
    assert isinstance(classify(FakeSdkError(400)), LLMBadRequest)
    assert isinstance(classify(FakeSdkError(404)), LLMBadRequest)
    assert isinstance(classify(TimeoutError("slow")), LLMUnavailable)
    plain = classify(RuntimeError("weird"))
    assert type(plain) is LLMError and not plain.retryable
    assert classify(FakeSdkError(429)).retryable and not classify(FakeSdkError(400)).retryable


def test_retry_policy_delay_is_capped_and_jittered() -> None:
    policy = RetryPolicy(base_delay_s=1.0, max_delay_s=5.0)
    rng = random.Random(0)
    delays = [policy.delay(attempt, rng) for attempt in (1, 2, 3, 4, 5)]
    assert all(0 <= d <= 5.0 for d in delays)
    assert policy.delay(1, random.Random(1)) <= 1.0


def test_with_retries_retries_only_retryable_errors() -> None:
    slept: list[float] = []
    attempts = iter([LLMRateLimited("429"), LLMUnavailable("503"), Completion("ok", "completed")])

    def operation() -> Completion:
        item = next(attempts)
        if isinstance(item, Exception):
            raise item
        return item

    result = with_retries(operation, RetryPolicy(max_attempts=4), sleep=slept.append, rng=random.Random(0))
    assert result.text == "ok" and result.attempts == 3 and len(slept) == 2

    with pytest.raises(LLMBadRequest):
        with_retries(lambda: (_ for _ in ()).throw(LLMBadRequest("400")), RetryPolicy(), sleep=slept.append)
    assert len(slept) == 2  # no sleep for a non-retryable error


def test_with_retries_gives_up_at_max_attempts_and_deadline() -> None:
    calls = {"n": 0}

    def always_429() -> Completion:
        calls["n"] += 1
        raise LLMRateLimited("429")

    with pytest.raises(LLMRateLimited):
        with_retries(always_429, RetryPolicy(max_attempts=3), sleep=lambda _: None, rng=random.Random(0))
    assert calls["n"] == 3

    ticks = iter([0.0, 100.0])  # the second clock read is already past the 90s deadline
    with pytest.raises(LLMUnavailable, match="deadline"):
        with_retries(always_429, RetryPolicy(max_attempts=5, total_deadline_s=90.0), sleep=lambda _: None, clock=lambda: next(ticks), rng=random.Random(0))


def test_fake_client_completes_and_streams() -> None:
    fake = FakeClient(script=["hello world", "streamed text"])
    assert fake.complete("hi").text == "hello world"
    assert "".join(fake.stream("hi")) == "streamed text"
    assert len(fake.calls) == 2


def test_cli_renders_markdown_from_a_file(tmp_path) -> None:
    article = tmp_path / "page.txt"
    article.write_text("Cargo-Lite 2.0 was released today with a shared build cache.", encoding="utf-8")
    fake = FakeClient(script=[json.dumps(VALID)])
    assert cli().main(["--file", str(article)], client=fake) == cli().EXIT_OK
    assert fake.calls[0]["response_format"] is not None and "<article>" in fake.calls[0]["prompt"]


def test_cli_json_flag_and_non_article_exit_code(tmp_path, capsys) -> None:
    page = tmp_path / "ad.txt"
    page.write_text("BUY NOW!!! 50% off everything", encoding="utf-8")
    code = cli().main(["--file", str(page), "--json"], client=FakeClient(script=[json.dumps(NOT_ARTICLE)]))
    assert code == cli().EXIT_NOT_ARTICLE
    assert json.loads(capsys.readouterr().out)["is_article"] is False


def test_cli_exit_codes_for_failures(tmp_path) -> None:
    assert cli().main(["--file", str(tmp_path / "missing.txt")], client=FakeClient()) == cli().EXIT_FETCH_FAILURE
    page = tmp_path / "page.txt"
    page.write_text("some text", encoding="utf-8")
    assert cli().main(["--file", str(page)], client=FakeClient(script=[LLMBadRequest("400")])) == cli().EXIT_LLM_FAILURE
    assert cli().main(["--file", str(page)], client=FakeClient(script=["{}", "{}"])) == cli().EXIT_LLM_FAILURE


def test_render_markdown_shapes() -> None:
    from ch09.schemas import ArticleSummary

    text = cli().render_markdown(ArticleSummary.model_validate(VALID), "https://example.com/x")
    assert text.startswith("### Cargo-Lite") and text.count("\n- ") == 3 and "Why it matters:" in text
    assert "does not look like an article" in cli().render_markdown(ArticleSummary.model_validate(NOT_ARTICLE), "x")
