"""Stage 3: structured summaries. One repair attempt, per-article isolation, stored once, traced and budgeted."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any
from pydantic import ValidationError
from morning_brief.budget import BudgetExceeded, BudgetGuard
from morning_brief.llm import prompts
from morning_brief.llm.client import LLMClient, LLMError, resilient_complete
from morning_brief.llm.schemas import ArticleSummary, response_format_for
from morning_brief.sources.base import Article
from morning_brief.store import Store
from morning_brief.tracing import Tracer, estimate_cost
SUMMARY_FORMAT = response_format_for(ArticleSummary)

@dataclass
class SummaryResult:
    summaries: dict[str, ArticleSummary] = field(default_factory=dict)
    reused: int = 0
    failures: list[str] = field(default_factory=list)
    budget_stopped: bool = False

def build_prompt(article: Article) -> str:
    raise NotImplementedError

def summarize_one(article: Article, client: LLMClient, system: str, *, fallback: LLMClient | None=None, tracer: Tracer | None=None, guard: BudgetGuard | None=None) -> tuple[ArticleSummary, dict[str, Any]]:
    """Ask, validate, repair once. Returns the summary and what it cost (all attempts, whichever model answered).

    Raises LLMError when primary and fallback both failed, ValidationError when two outputs were invalid.
    """
    raise NotImplementedError

def summarize_articles(articles: list[Article], client: LLMClient, store: Store, *, fallback: LLMClient | None=None, tracer: Tracer | None=None, guard: BudgetGuard | None=None, prompt_version: int=1, concurrency: int=3) -> SummaryResult:
    raise NotImplementedError
