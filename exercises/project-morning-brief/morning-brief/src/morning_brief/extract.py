"""Main-text extraction: polite, bounded, and tolerant. A failed article is a status, not an exception."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import httpx
import trafilatura

from morning_brief.sources.base import Article

MAX_CHARS = 6000
MIN_CHARS = 200


def extract_text(html: str) -> str:
    return (trafilatura.extract(html, include_comments=False, include_tables=False) or "").strip()


def fetch_and_extract(article: Article, http: httpx.Client, *, max_chars: int = MAX_CHARS) -> Article:
    try:
        response = http.get(article.url, timeout=10.0, follow_redirects=True, headers={"User-Agent": "morning-brief/0.1"})
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "html" not in content_type and "text" not in content_type:
            article.extract_status = f"skipped:{content_type.split(';')[0] or 'unknown'}"
            return _fallback(article)
        text = extract_text(response.text)
        if len(text) < MIN_CHARS:
            article.extract_status = "failed:too-short"
            return _fallback(article)
        article.text = text[:max_chars]
        article.extract_status = "ok"
        return article
    except Exception as exc:  # noqa: BLE001 - per-article isolation: the run continues with the feed blurb
        article.extract_status = f"failed:{type(exc).__name__}"
        return _fallback(article)


def _fallback(article: Article) -> Article:
    if not article.text and article.summary:
        article.text = article.summary[:MAX_CHARS]
    return article


def extract_all(articles: list[Article], http: httpx.Client, *, concurrency: int = 4) -> list[Article]:
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        return list(pool.map(lambda a: fetch_and_extract(a, http), articles))
