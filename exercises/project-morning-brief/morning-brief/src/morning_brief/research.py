"""Stage 6: the one agent in the pipeline. Bounded (steps, seconds, tokens), read-only tools, loop detection, traced.

The model picks which item to read; the code decides whether it may, how long, and how much.
"""

from __future__ import annotations

import json
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, Field, ValidationError

from morning_brief.budget import BudgetExceeded, BudgetGuard
from morning_brief.extract import extract_text
from morning_brief.llm import prompts
from morning_brief.llm.client import LLMClient, LLMError, classify
from morning_brief.llm.schemas import ResearchNote, clean_schema, response_format_for
from morning_brief.sources.base import Article

StopReason = Literal["answered", "max_steps", "timeout", "token_budget", "loop_detected", "budget", "error"]
URL = re.compile(r"https?://[^\s)\]>\"']+")


@dataclass
class Budgets:
    max_steps: int = 6
    max_seconds: float = 90.0
    max_tokens: int = 40_000


class AgentBackend(Protocol):
    model: str

    def create(self, *, history: list[dict[str, Any]], tools: list[dict[str, Any]], system: str) -> Any: ...


class GeminiAgentBackend:
    def __init__(self, model: str, timeout_s: float = 60.0) -> None:
        from google import genai
        from google.genai import types

        self.model = model
        self.client = genai.Client(http_options=types.HttpOptions(timeout=int(timeout_s * 1000), retry_options=types.HttpRetryOptions(attempts=1)))

    def create(self, *, history: list[dict[str, Any]], tools: list[dict[str, Any]], system: str) -> Any:
        try:
            return self.client.interactions.create(model=self.model, input=history, tools=tools, system_instruction=system, generation_config={"temperature": 0.2, "max_output_tokens": 600})
        except Exception as exc:
            raise classify(exc) from exc


# ---------------------------------------------------------------- tools


class SearchArgs(BaseModel):
    query: str = Field(description="Words to look for in today's item titles and summaries.")


class ReadArgs(BaseModel):
    item_id: str = Field(description="The id of a day item, as returned by search_items.")


class FetchArgs(BaseModel):
    url: str = Field(description="A link that appears inside an item you already read.")


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    args_model: type[BaseModel]
    func: Callable[..., Any]


def make_tools(day_items: list[Article], http: httpx.Client | None) -> dict[str, Tool]:
    by_id = {a.id: a for a in day_items}
    allowed_links: set[str] = set()

    def search_items(query: str) -> dict[str, Any]:
        words = [w for w in query.lower().split() if len(w) > 2]
        scored = []
        for a in day_items:
            hay = f"{a.title} {a.summary} {a.text[:400]}".lower()
            score = sum(1 for w in words if w in hay)
            if score:
                scored.append((score, a))
        scored.sort(key=lambda p: -p[0])
        return {"results": [{"id": a.id, "title": a.title, "source": a.source, "published_at": a.published_at} for _, a in scored[:5]]}

    def read_item(item_id: str) -> dict[str, Any]:
        a = by_id.get(item_id)
        if a is None:
            raise KeyError(f"no item {item_id!r} today")
        allowed_links.update(URL.findall(a.text))
        allowed_links.add(a.url)
        return {"id": a.id, "title": a.title, "url": a.url, "text": a.text[:4000]}

    def fetch_url(url: str) -> dict[str, Any]:
        if url not in allowed_links:  # policy first: the allowlist is checked before anything touches the network
            raise PermissionError("only links that appear in an item you read may be fetched")
        if urlparse(url).scheme not in ("http", "https"):
            raise PermissionError("only http(s)")
        if http is None:
            raise PermissionError("network is disabled in this run")
        response = http.get(url, timeout=10.0, follow_redirects=True, headers={"User-Agent": "morning-brief/0.1"})
        response.raise_for_status()
        return {"url": url, "text": extract_text(response.text)[:4000]}

    return {
        "search_items": Tool("search_items", "Search today's items by keywords. Returns ids and titles. Call this first.", SearchArgs, search_items),
        "read_item": Tool("read_item", "Read the full text of one of today's items by id.", ReadArgs, read_item),
        "fetch_url": Tool("fetch_url", "Download a page linked from an item you read. Only such links are allowed.", FetchArgs, fetch_url),
    }


def declarations(tools: dict[str, Tool]) -> list[dict[str, Any]]:
    return [{"type": "function", "name": t.name, "description": t.description, "parameters": clean_schema(t.args_model.model_json_schema())} for t in tools.values()]


def dispatch(tools: dict[str, Tool], name: str, arguments: dict[str, Any]) -> tuple[str, bool]:
    tool = tools.get(name)
    if tool is None:
        return json.dumps({"error": f"unknown tool {name!r}"}), True
    try:
        args = tool.args_model.model_validate(arguments)
    except ValidationError as exc:
        return json.dumps({"error": "invalid arguments", "details": exc.errors(include_url=False)}, default=str), True
    try:
        return json.dumps(tool.func(**args.model_dump()), ensure_ascii=False, default=str), False
    except Exception as exc:  # noqa: BLE001 - a failing tool becomes an error result the model can read
        return json.dumps({"error": f"{type(exc).__name__}: {exc}"}), True


# ---------------------------------------------------------------- the loop


@dataclass
class ResearchResult:
    story_id: str
    note: ResearchNote | None
    stop_reason: StopReason
    steps: int = 0
    tokens: int = 0
    seconds: float = 0.0
    sources: list[str] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)


def _tokens(interaction: Any) -> int:
    usage = getattr(interaction, "usage", None)
    return ((getattr(usage, "total_input_tokens", 0) or 0) + (getattr(usage, "total_output_tokens", 0) or 0)) if usage else 0


def research_story(story: Article, day_items: list[Article], backend: AgentBackend, structurer: LLMClient, *, http: httpx.Client | None = None, budgets: Budgets | None = None, guard: BudgetGuard | None = None, clock: Callable[[], float] = time.monotonic, prompt_version: int = 1) -> ResearchResult:
    budgets = budgets or Budgets()
    tools = make_tools(day_items, http)
    system = prompts.load("research", prompt_version).body
    question = f"Top story: {story.title} (id {story.id}). Add context and one key fact. Start by reading the story itself, then search for related items."
    history: list[dict[str, Any]] = [{"type": "user_input", "content": [{"type": "text", "text": question}]}]
    result = ResearchResult(story.id, None, "error")
    seen_calls: set[str] = set()
    started = clock()
    final_text = ""
    while True:
        result.seconds = clock() - started
        if result.steps >= budgets.max_steps:
            result.stop_reason = "max_steps"
            break
        if result.seconds >= budgets.max_seconds:
            result.stop_reason = "timeout"
            break
        if result.tokens >= budgets.max_tokens:
            result.stop_reason = "token_budget"
            break
        try:
            interaction = backend.create(history=history, tools=declarations(tools), system=system)
        except LLMError:
            result.stop_reason = "error"
            break
        result.steps += 1
        result.tokens += _tokens(interaction)
        if guard:
            try:
                usage = getattr(interaction, "usage", None)
                guard.charge(backend.model, input_tokens=(getattr(usage, "total_input_tokens", 0) or 0) if usage else 0, output_tokens=(getattr(usage, "total_output_tokens", 0) or 0) if usage else 0, stage="research")
            except BudgetExceeded:
                result.stop_reason = "budget"
                break
        calls = [s for s in (getattr(interaction, "steps", None) or []) if getattr(s, "type", None) == "function_call"]
        if not calls:
            final_text = (getattr(interaction, "output_text", "") or "").strip()
            result.stop_reason = "answered"
            break
        keys = [f"{c.name}:{json.dumps(dict(c.arguments or {}), sort_keys=True)}" for c in calls]
        if any(k in seen_calls for k in keys):
            result.stop_reason = "loop_detected"
            break
        seen_calls.update(keys)
        for call in calls:
            history.append({"type": "function_call", "id": call.id, "name": call.name, "arguments": dict(call.arguments or {})})
        for call in calls:
            output, is_error = dispatch(tools, call.name, dict(call.arguments or {}))
            result.tool_calls.append(f"{call.name}{'!' if is_error else ''}")
            history.append({"type": "function_result", "call_id": call.id, "name": call.name, "result": output, "is_error": is_error})
            if not is_error:
                source = dict(call.arguments or {}).get("item_id") or dict(call.arguments or {}).get("url")
                if source and source not in result.sources:
                    result.sources.append(str(source))
    if final_text and result.sources:
        result.note = _structure(final_text, result.sources, structurer, guard)
    result.seconds = clock() - started
    return result


def _structure(text: str, sources: list[str], client: LLMClient, guard: BudgetGuard | None) -> ResearchNote | None:
    """One cheap structured call turns the agent's prose into a ResearchNote; sources come from the tools, not the model."""
    try:
        completion = client.complete(f"<notes>\n{text}\n</notes>\nsources read: {', '.join(sources)}", system="Convert the research notes into the JSON schema. Use only what the notes say. source_ids must be exactly the sources read.", max_output_tokens=300, temperature=0.0, response_format=response_format_for(ResearchNote))
        if guard:
            guard.charge(client.model, input_tokens=completion.input_tokens, output_tokens=completion.output_tokens, stage="research")
        note = ResearchNote.model_validate_json(completion.text)
        note.source_ids = sources  # the code knows what was read; the model's list is not trusted
        return note
    except (LLMError, ValidationError, BudgetExceeded):
        return None
