"""Trust boundaries in code: links only from fetched sources, no raw HTML from the model, redaction for logs."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from morning_brief.compose import Issue

URL = re.compile(r"https?://[^\s)\]>\"']+")
HTML_TAG = re.compile(r"<\s*/?\s*(script|iframe|img|a|style|object|embed|form|input)\b[^>]*>", re.IGNORECASE)
INSTRUCTION_ECHO = re.compile(r"\b(as instructed|ignore (all |the )?(previous|above) instructions|system prompt|you are now)\b", re.IGNORECASE)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
KEYS = re.compile(r"AIza[0-9A-Za-z\-_]{35}|\bsk-[A-Za-z0-9_\-]{20,}|\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}")


@dataclass
class PolicyResult:
    violations: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations


def check_model_text(text: str) -> PolicyResult:
    """Applied to every string the model wrote: no links at all (links come from code), no HTML, no echoes."""
    result = PolicyResult()
    if URL.search(text):
        result.violations.append("link in model text")
    if HTML_TAG.search(text):
        result.violations.append("HTML tag in model text")
    if INSTRUCTION_ECHO.search(text):
        result.violations.append("instruction echo in model text")
    return result


def scrub_model_text(text: str) -> str:
    text = URL.sub("[link removed]", text)
    return HTML_TAG.sub("", text)


def check_issue(issue: Issue, rendered_markdown: str) -> PolicyResult:
    """Every link in the rendered issue must be one the code put there from fetched sources."""
    result = PolicyResult()
    allowed = issue.all_urls()
    foreign = sorted({u.rstrip(".,;") for u in URL.findall(rendered_markdown)} - allowed)
    if foreign:
        result.violations.append(f"links not from sources: {foreign}")
    for item in issue.top_stories + issue.more_stories:
        for text in (item.headline, item.why_it_matters, *item.bullets, *( [item.research.context, item.research.key_fact] if item.research else [])):
            result.violations.extend(f"{item.article_id}: {v}" for v in check_model_text(text).violations)
    for item in issue.top_stories + issue.more_stories:
        if urlparse(item.url).scheme not in ("http", "https"):
            result.violations.append(f"{item.article_id}: non-http source url")
    return result


def redact(text: str) -> str:
    return EMAIL.sub("[email]", KEYS.sub("[key]", text))
