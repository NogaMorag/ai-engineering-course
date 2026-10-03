"""Chapter 10 solution: two tools the model may ask for, and a dispatcher that never trusts it.

fetch_url(url)                 download a public web page and extract its main text
search_notes(query, max_results) case-insensitive search over the markdown notes in data/notes

The model only *proposes* a call. dispatch() checks the tool exists, validates the arguments with
Pydantic, runs the function, and turns any failure into an error result the model can read.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
import trafilatura
from pydantic import BaseModel, Field, ValidationError

from ch09.schemas import clean_schema

NOTES_DIR = Path(__file__).parent / "data" / "notes"
MAX_TEXT_CHARS = 6000
BLOCKED_HOSTS = ("localhost", "127.", "10.", "192.168.", "169.254.", "0.", "::1")


class FetchUrlArgs(BaseModel):
    url: str = Field(description="Absolute http or https URL of a public web page.")


class SearchNotesArgs(BaseModel):
    query: str = Field(description="Words to look for in the user's notes (case-insensitive).")
    max_results: int = Field(default=5, ge=1, le=10, description="Maximum number of matching lines to return.")


def validate_public_http_url(url: str) -> str:
    """Reject anything that is not a public http(s) URL. A real deployment also resolves DNS first."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("only http and https URLs are allowed")
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("the URL has no host")
    if host.startswith(BLOCKED_HOSTS) or host.endswith((".local", ".internal")):
        raise ValueError("private or local hosts are not allowed")
    if host.startswith("172."):
        second = host.split(".")[1] if "." in host else ""
        if second.isdigit() and 16 <= int(second) <= 31:
            raise ValueError("private hosts are not allowed")
    return url


def fetch_url(url: str) -> dict[str, Any]:
    validate_public_http_url(url)
    response = httpx.get(url, timeout=10.0, follow_redirects=True, headers={"User-Agent": "ai-course-exercise/1.0"})
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "html" not in content_type and "text" not in content_type:
        raise ValueError(f"unsupported content type: {content_type or 'unknown'}")
    text = trafilatura.extract(response.text, include_comments=False) or ""
    title_match = re.search(r"<title[^>]*>(.*?)</title>", response.text, re.IGNORECASE | re.DOTALL)
    return {
        "url": str(response.url),
        "status_code": response.status_code,
        "title": " ".join(title_match.group(1).split()) if title_match else "",
        "text": text[:MAX_TEXT_CHARS],
        "truncated": len(text) > MAX_TEXT_CHARS,
    }


def search_notes(query: str, max_results: int = 5) -> dict[str, Any]:
    needle = query.lower().strip()
    if not needle:
        raise ValueError("the query is empty")
    matches: list[dict[str, Any]] = []
    for path in sorted(NOTES_DIR.glob("*.md")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if needle in line.lower():
                matches.append({"file": path.name, "line": number, "text": line.strip()})
                if len(matches) >= max_results:
                    return {"query": query, "matches": matches, "more": True}
    return {"query": query, "matches": matches, "more": False}


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    args_model: type[BaseModel]
    func: Callable[..., dict[str, Any]]


TOOLS: dict[str, Tool] = {
    tool.name: tool
    for tool in (
        Tool(
            "fetch_url",
            "Downloads a public web page and returns its title and main text (up to 6000 characters). "
            "Use it when the user gives a URL or asks about a specific page. Does not work on private hosts.",
            FetchUrlArgs,
            fetch_url,
        ),
        Tool(
            "search_notes",
            "Searches the user's personal markdown notes for lines containing the query. "
            "Returns matching lines with file names. Use it for questions about what the user wrote down.",
            SearchNotesArgs,
            search_notes,
        ),
    )
}


def tool_declarations() -> list[dict[str, Any]]:
    """What the model sees: name, description, and the JSON schema of the arguments."""
    return [
        {
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": clean_schema(tool.args_model.model_json_schema()),
        }
        for tool in TOOLS.values()
    ]


def dispatch(name: str, arguments: dict[str, Any]) -> tuple[str, bool]:
    """Run a proposed tool call safely. Returns (json_result, is_error)."""
    tool = TOOLS.get(name)
    if tool is None:
        return json.dumps({"error": f"unknown tool {name!r}"}), True
    try:
        args = tool.args_model.model_validate(arguments)
    except ValidationError as exc:
        return json.dumps({"error": "invalid arguments", "details": exc.errors(include_url=False)}, default=str), True
    try:
        result = tool.func(**args.model_dump())
    except Exception as exc:  # noqa: BLE001 - a failing tool must become an error result, never crash the loop
        return json.dumps({"error": f"{type(exc).__name__}: {exc}"}), True
    return json.dumps(result, ensure_ascii=False), False
