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
StopReason = Literal['answered', 'max_steps', 'timeout', 'token_budget', 'loop_detected', 'budget', 'error']
URL = re.compile('https?://[^\\s)\\]>\\"\']+')

@dataclass
class Budgets:
    max_steps: int = 6
    max_seconds: float = 90.0
    max_tokens: int = 40000

class AgentBackend(Protocol):
    model: str

    def create(self, *, history: list[dict[str, Any]], tools: list[dict[str, Any]], system: str) -> Any:
        raise NotImplementedError

class GeminiAgentBackend:

    def __init__(self, model: str, timeout_s: float=60.0) -> None:
        raise NotImplementedError

    def create(self, *, history: list[dict[str, Any]], tools: list[dict[str, Any]], system: str) -> Any:
        raise NotImplementedError

class SearchArgs(BaseModel):
    query: str = Field(description="Words to look for in today's item titles and summaries.")

class ReadArgs(BaseModel):
    item_id: str = Field(description='The id of a day item, as returned by search_items.')

class FetchArgs(BaseModel):
    url: str = Field(description='A link that appears inside an item you already read.')

@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    args_model: type[BaseModel]
    func: Callable[..., Any]

def make_tools(day_items: list[Article], http: httpx.Client | None) -> dict[str, Tool]:
    raise NotImplementedError

def declarations(tools: dict[str, Tool]) -> list[dict[str, Any]]:
    raise NotImplementedError

def dispatch(tools: dict[str, Tool], name: str, arguments: dict[str, Any]) -> tuple[str, bool]:
    raise NotImplementedError

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
    raise NotImplementedError

def research_story(story: Article, day_items: list[Article], backend: AgentBackend, structurer: LLMClient, *, http: httpx.Client | None=None, budgets: Budgets | None=None, guard: BudgetGuard | None=None, clock: Callable[[], float]=time.monotonic, prompt_version: int=1) -> ResearchResult:
    raise NotImplementedError

def _structure(text: str, sources: list[str], client: LLMClient, guard: BudgetGuard | None) -> ResearchNote | None:
    """One cheap structured call turns the agent's prose into a ResearchNote; sources come from the tools, not the model."""
    raise NotImplementedError
