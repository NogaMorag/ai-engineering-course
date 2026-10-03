"""Hacker News front page through the public Algolia API. Parsing is pure; fetching is one GET."""

from __future__ import annotations

from typing import Any

import httpx

from morning_brief.config import SourceSpec
from morning_brief.sources.base import Article

API = "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30"


def parse_hn(payload: dict[str, Any], source: str = "hn") -> list[Article]:
    articles = []
    for hit in payload.get("hits", []):
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        title = hit.get("title")
        if not title:
            continue
        points = hit.get("points") or 0
        articles.append(Article.create(url=url, source=source, title=title, published_at=hit.get("created_at"), summary=f"{points} points on Hacker News"))
    return articles


def collect_hn(spec: SourceSpec, http: httpx.Client) -> list[Article]:
    response = http.get(spec.url or API, timeout=15.0, headers={"User-Agent": "morning-brief/0.1"})
    response.raise_for_status()
    return parse_hn(response.json(), spec.name)
