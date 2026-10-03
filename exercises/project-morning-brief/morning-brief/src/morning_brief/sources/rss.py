"""RSS / Atom through feedparser. Parsing is pure (bytes in, articles out) so fixtures can drive the tests."""

from __future__ import annotations

import calendar
import datetime as dt

import feedparser
import httpx

from morning_brief.config import SourceSpec
from morning_brief.sources.base import Article

MAX_ENTRIES = 50


def _published(entry) -> str | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return dt.datetime.fromtimestamp(calendar.timegm(parsed), tz=dt.UTC).isoformat(timespec="seconds")


def parse_feed(content: bytes, source: str) -> list[Article]:
    feed = feedparser.parse(content)
    articles = []
    for entry in feed.entries[:MAX_ENTRIES]:
        link = entry.get("link")
        title = entry.get("title")
        if not link or not title:
            continue
        articles.append(Article.create(url=link, source=source, title=title, published_at=_published(entry), summary=entry.get("summary", "")))
    return articles


def fetch_feed(url: str, http: httpx.Client) -> bytes:
    response = http.get(url, timeout=15.0, follow_redirects=True, headers={"User-Agent": "morning-brief/0.1"})
    response.raise_for_status()
    return response.content


def collect_rss(spec: SourceSpec, http: httpx.Client) -> list[Article]:
    if not spec.url:
        raise ValueError(f"source {spec.name} has no url")
    return parse_feed(fetch_feed(spec.url, http), spec.name)
