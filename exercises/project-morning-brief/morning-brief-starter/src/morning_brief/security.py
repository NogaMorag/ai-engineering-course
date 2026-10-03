"""Trust boundaries in code: links only from fetched sources, no raw HTML from the model, redaction for logs."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse
from morning_brief.compose import Issue
URL = re.compile('https?://[^\\s)\\]>\\"\']+')
HTML_TAG = re.compile('<\\s*/?\\s*(script|iframe|img|a|style|object|embed|form|input)\\b[^>]*>', re.IGNORECASE)
INSTRUCTION_ECHO = re.compile('\\b(as instructed|ignore (all |the )?(previous|above) instructions|system prompt|you are now)\\b', re.IGNORECASE)
EMAIL = re.compile('[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}')
KEYS = re.compile('AIza[0-9A-Za-z\\-_]{35}|\\bsk-[A-Za-z0-9_\\-]{20,}|\\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}')

@dataclass
class PolicyResult:
    violations: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        raise NotImplementedError

def check_model_text(text: str) -> PolicyResult:
    """Applied to every string the model wrote: no links at all (links come from code), no HTML, no echoes."""
    raise NotImplementedError

def scrub_model_text(text: str) -> str:
    raise NotImplementedError

def check_issue(issue: Issue, rendered_markdown: str) -> PolicyResult:
    """Every link in the rendered issue must be one the code put there from fetched sources."""
    raise NotImplementedError

def redact(text: str) -> str:
    raise NotImplementedError
