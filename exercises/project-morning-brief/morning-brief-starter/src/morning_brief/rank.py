"""Stage 4: relevance for one specific reader. The model scores with a reason; code applies the rules it is better at."""
from __future__ import annotations
import datetime as dt
import math
from dataclasses import dataclass, field
from pydantic import ValidationError
from morning_brief.budget import BudgetExceeded, BudgetGuard
from morning_brief.config import Profile
from morning_brief.llm import prompts
from morning_brief.llm.client import LLMClient, resilient_complete
from morning_brief.llm.schemas import ArticleSummary, Relevance, response_format_for
from morning_brief.sources.base import Article
RELEVANCE_FORMAT = response_format_for(Relevance)

@dataclass
class Scored:
    article_id: str
    llm_score: int
    reason: str
    boosts: dict[str, float] = field(default_factory=dict)

    @property
    def final(self) -> float:
        raise NotImplementedError

def rule_boosts(article: Article, summary: ArticleSummary, profile: Profile, *, now: dt.datetime) -> dict[str, float]:
    """What code decides better than a model: source weight, recency decay, skip topics, keyword hits."""
    raise NotImplementedError

def build_prompt(summary: ArticleSummary, article: Article) -> str:
    raise NotImplementedError

def score_articles(items: list[tuple[Article, ArticleSummary]], profile: Profile, client: LLMClient, *, fallback: LLMClient | None=None, guard: BudgetGuard | None=None, now: dt.datetime | None=None, prompt_version: int=1) -> tuple[list[Scored], list[str]]:
    raise NotImplementedError
