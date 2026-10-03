"""Sources: each one turns a feed into Article rows and never raises past `collect`."""
from __future__ import annotations
from collections.abc import Callable
import httpx
from morning_brief.config import Profile, SourceSpec
from morning_brief.sources.base import Article
from morning_brief.sources.hn import collect_hn
from morning_brief.sources.rss import collect_rss
Collector = Callable[[SourceSpec, httpx.Client], list[Article]]
COLLECTORS: dict[str, Collector] = {'rss': collect_rss, 'hn': collect_hn}

def collect(profile: Profile, http: httpx.Client, *, collectors: dict[str, Collector] | None=None) -> tuple[list[Article], list[str]]:
    """Run every source; a failing source is a line in `failures`, never an exception (N3)."""
    raise NotImplementedError
