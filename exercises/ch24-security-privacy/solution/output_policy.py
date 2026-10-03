"""Chapter 24 solution: what the model wrote is untrusted output. Check it before anyone sees it.

Prompt injection reaches the user through the output: a smuggled link, a planted instruction, raw
HTML. The policy enforces what the prompt can only ask for.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

URL = re.compile(r"https?://[^\s)\]>\"']+")
HTML_TAG = re.compile(r"<\s*/?\s*(script|iframe|img|a|style|object|embed|form|input)\b[^>]*>", re.IGNORECASE)
INSTRUCTION_ECHO = re.compile(r"\b(as instructed|ignore (all |the )?(previous|above) instructions|system prompt|you are now)\b", re.IGNORECASE)


@dataclass
class PolicyResult:
    violations: list[str] = field(default_factory=list)
    foreign_links: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations


def links_in(text: str) -> list[str]:
    return [u.rstrip(".,;") for u in URL.findall(text)]


def host_of(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def check_output(output: str, *, source_text: str, allowed_hosts: set[str] | None = None) -> PolicyResult:
    """Links must come from the source (or an allowlist); no HTML; no echoes of injected instructions."""
    result = PolicyResult()
    source_links = set(links_in(source_text))
    allowed_hosts = {h.lower() for h in (allowed_hosts or set())}
    for link in links_in(output):
        if link not in source_links and host_of(link) not in allowed_hosts:
            result.foreign_links.append(link)
    if result.foreign_links:
        result.violations.append(f"links not present in the source: {result.foreign_links}")
    if HTML_TAG.search(output):
        result.violations.append("HTML tags in the output")
    if INSTRUCTION_ECHO.search(output):
        result.violations.append("the output echoes an injected instruction")
    return result


def strip_foreign_links(output: str, *, source_text: str, allowed_hosts: set[str] | None = None) -> str:
    """Defense in depth: remove links the policy would reject instead of discarding the whole output."""
    verdict = check_output(output, source_text=source_text, allowed_hosts=allowed_hosts)
    cleaned = output
    for link in verdict.foreign_links:
        cleaned = cleaned.replace(link, "[link removed]")
    return cleaned
