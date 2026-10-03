from __future__ import annotations

import json
from pathlib import Path

import httpx

from morning_brief.config import SourceSpec
from morning_brief.sources import collect
from morning_brief.sources.base import Article, article_id, canonical_url
from morning_brief.sources.hn import parse_hn
from morning_brief.sources.rss import parse_feed
from morning_brief.store import Store

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def test_canonical_url_and_id_are_stable() -> None:
    a = canonical_url("HTTPS://Example.com/devwire/cargo-lite-2/?utm_source=rss&b=2&a=1#top")
    b = canonical_url("https://example.com/devwire/cargo-lite-2?a=1&b=2")
    assert a == b == "https://example.com/devwire/cargo-lite-2?a=1&b=2"
    assert article_id(a) == article_id(b) and len(article_id(a)) == 16
    assert canonical_url("https://example.com/") == "https://example.com/"


def test_parse_feed_and_hn_skip_broken_entries() -> None:
    articles = parse_feed((FIXTURES / "devwire.xml").read_bytes(), "devwire")
    assert len(articles) == 5 and articles[0].title.startswith("Cargo-Lite") and articles[0].published_at == "2026-09-29T07:00:00+00:00"
    assert articles[0].canonical_url == "https://example.com/devwire/cargo-lite-2" and "Cargo-Lite 2.0 was released" in articles[0].summary
    hn = parse_hn(json.loads((FIXTURES / "hn.json").read_text(encoding="utf-8")))
    assert len(hn) == 4 and hn[3].url.startswith("https://news.ycombinator.com/item?id=104") and "95 points" in hn[3].summary
    assert parse_feed(b"not xml at all", "x") == []


def test_collect_isolates_a_dead_feed(profile) -> None:
    def rss(spec: SourceSpec, http: httpx.Client):
        if spec.name == "stackdaily":
            raise httpx.ConnectError("boom")
        return parse_feed((FIXTURES / f"{spec.name}.xml").read_bytes(), spec.name)

    def hn(spec, http):
        return parse_hn(json.loads((FIXTURES / "hn.json").read_text(encoding="utf-8")), spec.name)

    articles, failures = collect(profile, httpx.Client(), collectors={"rss": rss, "hn": hn})
    assert len(articles) == 9 and failures == ["stackdaily: ConnectError: boom"]


def test_store_ingestion_and_delivery_are_idempotent(tmp_path: Path) -> None:
    store = Store(tmp_path / "db" / "brief.sqlite")
    articles = parse_feed((FIXTURES / "devwire.xml").read_bytes(), "devwire")
    assert store.upsert_articles(articles) == 5
    assert store.upsert_articles(articles) == 0 and store.count_articles() == 5
    a = articles[0]
    a.text, a.extract_status = "full text", "ok"
    store.update_extraction(a)
    assert store.get_article(a.id).extract_status == "ok" and store.get_article("nope") is None
    store.save_summary(a.id, '{"x": 1}', model="m", tokens_in=1, tokens_out=1, cost=0.0)
    assert store.get_summary(a.id) == '{"x": 1}' and store.get_summary(articles[1].id) is None
    assert store.record_delivery("run-2026-10-03", "file", "k") is True
    assert store.record_delivery("run-2026-10-03", "file", "k") is False and store.delivered("run-2026-10-03", "file")
    store.start_run("run-2026-10-03", "2026-10-03")
    store.finish_run("run-2026-10-03", "ok", 0.01, {"a": 1})
    assert store.get_run("run-2026-10-03")["status"] == "ok"
    assert Article.from_dict(a.as_dict()) == a
