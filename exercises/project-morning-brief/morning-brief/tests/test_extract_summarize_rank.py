from __future__ import annotations

import datetime as dt
import json
import sqlite3
from pathlib import Path

import httpx

from morning_brief.budget import BudgetGuard
from morning_brief.extract import extract_text, fetch_and_extract
from morning_brief.llm.client import FakeClient, LLMUnavailable
from morning_brief.llm.schemas import ArticleSummary
from morning_brief.rank import rule_boosts, score_articles
from morning_brief.sources.base import Article
from morning_brief.sources.rss import parse_feed
from morning_brief.store import Store
from morning_brief.summarize import summarize_articles, summarize_one
from morning_brief.tracing import Tracer, read_spans

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
HTML = (Path(__file__).parent / "fixtures" / "article.html").read_text(encoding="utf-8")
VALID = {"is_article": True, "headline": "Cargo-Lite 2.0 ships a shared build cache", "bullets": ["Released Tuesday.", "Builds from 41 to 6 minutes.", "Old config removed in 3.0."], "why_it_matters": "Why it matters: faster Rust builds.", "tags": ["rust"], "confidence": "high"}


def mock_http() -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("cargo-lite-2"):
            return httpx.Response(200, text=HTML, headers={"content-type": "text/html; charset=utf-8"})
        if request.url.path.endswith("payments-postmortem"):
            return httpx.Response(404)
        return httpx.Response(200, content=b"%PDF-1.4", headers={"content-type": "application/pdf"})

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_extraction_statuses_and_fallbacks() -> None:
    assert "shared build cache" in extract_text(HTML) and "Home | About" not in extract_text(HTML)
    articles = parse_feed((FIXTURES / "devwire.xml").read_bytes(), "devwire")
    http = mock_http()
    ok = fetch_and_extract(articles[0], http)
    assert ok.extract_status == "ok" and len(ok.text) > 200
    missing = fetch_and_extract(articles[1], http)
    assert missing.extract_status.startswith("failed:HTTPStatusError") and missing.text == missing.summary  # the blurb stands in
    pdf = fetch_and_extract(articles[2], http)
    assert pdf.extract_status == "skipped:application/pdf" and pdf.text


def test_summarize_repairs_once_reuses_stored_and_isolates_failures(tmp_path: Path) -> None:
    store = Store(tmp_path / "brief.sqlite")
    articles = parse_feed((FIXTURES / "devwire.xml").read_bytes(), "devwire")[:3]
    for a in articles:
        a.text = a.summary
    store.save_summary(articles[2].id, json.dumps({**VALID, "headline": "stored earlier"}), model="m", tokens_in=0, tokens_out=0, cost=0)
    fake = FakeClient(script=["not json", json.dumps(VALID), LLMUnavailable("503")])
    tracer = Tracer(tmp_path / "t.jsonl")
    result = summarize_articles(articles, fake, store, tracer=tracer, guard=BudgetGuard(1.0), concurrency=1)
    assert result.reused == 1 and result.summaries[articles[2].id].headline == "stored earlier"
    assert result.summaries[articles[0].id].headline.startswith("Cargo-Lite") and "rejected by the validator" in fake.calls[1]["prompt"]
    assert len(result.failures) == 1 and "LLMUnavailable" in result.failures[0]
    assert store.get_summary(articles[0].id) is not None and store.get_summary(articles[1].id) is None
    events = [s for s in read_spans(tracer.path) if s["name"] == "summarize.call"]
    assert len(events) == 2 and events[0]["attempt"] == 1 and events[1]["attempt"] == 2


def test_summarize_one_gives_up_after_two_invalid_outputs() -> None:
    a = Article.create(url="https://example.com/x", source="devwire", title="t", published_at=None, summary="s")
    a.text = "some text"
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        summarize_one(a, FakeClient(script=["{}", "{}"]), system="s")


def test_rule_boosts_and_scoring(profile) -> None:
    now = dt.datetime(2026, 10, 3, 7, 0, tzinfo=dt.UTC)
    articles = parse_feed((FIXTURES / "devwire.xml").read_bytes(), "devwire")
    cargo = ArticleSummary.model_validate(VALID)
    boosts = rule_boosts(articles[0], cargo, profile, now=now)
    assert boosts["source_weight"] == 0.0 and 0 < boosts["recency"] < 10 and boosts["keyword_hits"] >= 5 and "skip_topic" not in boosts
    sports = ArticleSummary.model_validate({**VALID, "headline": "Local football derby ends in a draw", "tags": ["sports"]})
    assert rule_boosts(articles[4], sports, profile, now=now)["skip_topic"] == -100.0

    fake = FakeClient(script=[json.dumps({"score": 85, "reason": "rust tooling", "matched_topics": ["rust and build tooling"]}), LLMUnavailable("503")])
    scored, failures = score_articles([(articles[0], cargo), (articles[4], sports), (articles[1], ArticleSummary.model_validate({**VALID, "headline": "Payments database postmortem", "tags": ["databases"]}))], profile, fake, now=now)
    assert next(s.article_id for s in scored) == articles[0].id and scored[0].llm_score == 85 and scored[0].final > 85
    assert scored[-1].reason == "skip topic" and scored[-1].final == 0.0
    assert len(failures) == 1 and any(s.reason.startswith("scoring failed") and s.llm_score == 50 for s in scored)
    assert fake.calls[0]["system"].startswith("<reader_profile>")  # the profile is the stable prefix


def test_summarize_falls_back_to_the_second_model_and_stores_real_usage(tmp_path: Path) -> None:
    store = Store(tmp_path / "brief.sqlite")
    article = parse_feed((FIXTURES / "devwire.xml").read_bytes(), "devwire")[0]
    article.text = article.summary
    primary, fallback = FakeClient(script=[LLMUnavailable("503")], model="fast"), FakeClient(script=[json.dumps(VALID)], model="smart")
    tracer = Tracer(tmp_path / "t.jsonl")
    result = summarize_articles([article], primary, store, fallback=fallback, tracer=tracer, concurrency=1)
    assert not result.failures and result.summaries[article.id].headline.startswith("Cargo-Lite")
    event = [s for s in read_spans(tracer.path) if s["name"] == "summarize.call"][-1]
    assert event["source"] == "fallback" and event["model"] == "smart"
    model, tokens_in, tokens_out = sqlite3.connect(tmp_path / "brief.sqlite").execute("SELECT model, tokens_in, tokens_out FROM summaries").fetchone()
    assert model == "smart" and tokens_in > 0 and tokens_out > 0  # no more zero columns
