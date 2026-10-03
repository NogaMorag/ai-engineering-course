"""The Article row and the canonical id that makes ingestion idempotent."""

from __future__ import annotations

import datetime as dt
import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PREFIXES = ("utm_", "fbclid", "gclid", "mc_", "ref", "source")


def canonical_url(url: str) -> str:
    """Lowercase scheme and host, drop tracking parameters and the fragment, drop a trailing slash."""
    parts = urlsplit(url.strip())
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not k.lower().startswith(TRACKING_PREFIXES)]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(sorted(query)), ""))


def article_id(canonical: str) -> str:
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


@dataclass
class Article:
    id: str
    url: str
    canonical_url: str
    source: str
    title: str
    published_at: str | None  # ISO 8601, UTC
    summary: str = ""  # the feed's own blurb, used as a fallback for extraction
    text: str = ""
    fetched_at: str = field(default_factory=lambda: dt.datetime.now(tz=dt.UTC).isoformat(timespec="seconds"))
    extract_status: str = "pending"

    @classmethod
    def create(cls, *, url: str, source: str, title: str, published_at: str | None, summary: str = "") -> Article:
        canonical = canonical_url(url)
        return cls(id=article_id(canonical), url=url, canonical_url=canonical, source=source, title=title.strip(), published_at=published_at, summary=summary.strip())

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Article:
        return cls(**data)
