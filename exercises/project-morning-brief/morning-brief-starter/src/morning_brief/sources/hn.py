"""Hacker News front page through the public Algolia API. Parsing is pure; fetching is one GET."""
from __future__ import annotations
from typing import Any
import httpx
from morning_brief.config import SourceSpec
from morning_brief.sources.base import Article
API = 'https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30'

def parse_hn(payload: dict[str, Any], source: str='hn') -> list[Article]:
    raise NotImplementedError

def collect_hn(spec: SourceSpec, http: httpx.Client) -> list[Article]:
    raise NotImplementedError
