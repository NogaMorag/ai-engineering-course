"""Stage 7: from structured inputs to the Newsletter model. Code composes; the model writes two sentences."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field, ValidationError
from morning_brief.budget import BudgetExceeded, BudgetGuard
from morning_brief.config import Profile
from morning_brief.llm import prompts
from morning_brief.llm.client import LLMClient, LLMError, resilient_complete
from morning_brief.llm.schemas import ArticleSummary, IssueIntro, ResearchNote, response_format_for
from morning_brief.memory import FollowUp
from morning_brief.sources.base import Article

class IssueItem(BaseModel):
    article_id: str
    title: str
    headline: str
    bullets: list[str]
    why_it_matters: str
    url: str
    source: str
    score: float
    reason: str
    also_covered: list[dict[str, str]] = Field(default_factory=list)
    follow_up_of: dict[str, Any] | None = None
    research: ResearchNote | None = None

class Issue(BaseModel):
    date: str
    language: str
    greeting_line: str
    theme: str
    top_stories: list[IssueItem]
    more_stories: list[IssueItem]
    skipped_note: str = ''
    metadata: dict[str, Any] = Field(default_factory=dict)

    def all_urls(self) -> set[str]:
        raise NotImplementedError

def build_item(article: Article, summary: ArticleSummary, *, score: float, reason: str, members: list[Article], follow_up: FollowUp | None, research: ResearchNote | None) -> IssueItem:
    raise NotImplementedError

def write_intro(date: str, profile: Profile, headlines: list[str], client: LLMClient, *, fallback: LLMClient | None=None, guard: BudgetGuard | None=None, prompt_version: int=1) -> IssueIntro:
    """The only model call in composition: primary, then the fallback model, then a plain greeting. The issue always goes out."""
    raise NotImplementedError

def compose_issue(date: str, profile: Profile, top: list[IssueItem], more: list[IssueItem], intro: IssueIntro, *, metadata: dict[str, Any], skipped_note: str='') -> Issue:
    raise NotImplementedError
