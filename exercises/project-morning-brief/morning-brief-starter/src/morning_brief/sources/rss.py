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
    raise NotImplementedError

def parse_feed(content: bytes, source: str) -> list[Article]:
    raise NotImplementedError

def fetch_feed(url: str, http: httpx.Client) -> bytes:
    raise NotImplementedError

def collect_rss(spec: SourceSpec, http: httpx.Client) -> list[Article]:
    raise NotImplementedError
