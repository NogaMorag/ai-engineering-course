"""Main-text extraction: polite, bounded, and tolerant. A failed article is a status, not an exception."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import httpx
import trafilatura
from morning_brief.sources.base import Article
MAX_CHARS = 6000
MIN_CHARS = 200

def extract_text(html: str) -> str:
    raise NotImplementedError

def fetch_and_extract(article: Article, http: httpx.Client, *, max_chars: int=MAX_CHARS) -> Article:
    raise NotImplementedError

def _fallback(article: Article) -> Article:
    raise NotImplementedError

def extract_all(articles: list[Article], http: httpx.Client, *, concurrency: int=4) -> list[Article]:
    raise NotImplementedError
