"""Stage 4: relevance for one specific reader. The model scores with a reason; code applies the rules it is better at."""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass, field

from pydantic import ValidationError

from morning_brief.budget import BudgetExceeded, BudgetGuard
from morning_brief.config import Profile
from morning_brief.llm import prompts
from morning_brief.llm.client import LLMClient, LLMError
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
        return max(0.0, self.llm_score + sum(self.boosts.values()))


def rule_boosts(article: Article, summary: ArticleSummary, profile: Profile, *, now: dt.datetime) -> dict[str, float]:
    """What code decides better than a model: source weight, recency decay, skip topics, keyword hits."""
    boosts: dict[str, float] = {}
    source = next((s for s in profile.sources if s.name == article.source), None)
    if source:
        boosts["source_weight"] = round((source.weight - 1.0) * 20, 1)  # weight 0.8 -> -4, weight 1.2 -> +4
    if article.published_at:
        age_hours = max(0.0, (now - dt.datetime.fromisoformat(article.published_at)).total_seconds() / 3600)
        boosts["recency"] = round(10 * math.exp(-age_hours / 36), 1)  # +10 fresh, ~+5 after a day and a half
    haystack = f"{article.title} {summary.headline} {' '.join(summary.tags)}".lower()
    if any(skip.lower() in haystack for skip in profile.skip_topics):
        boosts["skip_topic"] = -100.0
    hits = sum(1 for topic in profile.topics for keyword in topic.keywords if keyword.lower() in haystack)
    if hits:
        boosts["keyword_hits"] = min(15.0, 5.0 * hits)
    return boosts


def build_prompt(summary: ArticleSummary, article: Article) -> str:
    bullets = "\n".join(f"- {b}" for b in summary.bullets)
    return f"<item>\ntitle: {article.title}\nheadline: {summary.headline}\n{bullets}\n{summary.why_it_matters}\ntags: {', '.join(summary.tags)}\n</item>"


def score_articles(items: list[tuple[Article, ArticleSummary]], profile: Profile, client: LLMClient, *, guard: BudgetGuard | None = None, now: dt.datetime | None = None, prompt_version: int = 1) -> tuple[list[Scored], list[str]]:
    now = now or dt.datetime.now(tz=dt.UTC)
    system = prompts.render(prompts.load("score", prompt_version), profile=profile.as_prompt_block())
    scored: list[Scored] = []
    failures: list[str] = []
    for article, summary in items:
        if not summary.is_article:
            continue
        boosts = rule_boosts(article, summary, profile, now=now)
        if boosts.get("skip_topic"):
            scored.append(Scored(article.id, 0, "skip topic", boosts))
            continue
        try:
            completion = client.complete(build_prompt(summary, article), system=system, max_output_tokens=200, temperature=0.0, response_format=RELEVANCE_FORMAT)
            if guard:
                guard.charge(client.model, input_tokens=completion.input_tokens, output_tokens=completion.output_tokens, cached_tokens=completion.cached_tokens, stage="score")
            relevance = Relevance.model_validate_json(completion.text)
            scored.append(Scored(article.id, relevance.score, relevance.reason, boosts))
        except BudgetExceeded as exc:
            failures.append(f"{article.id}: budget: {exc}")
            scored.append(Scored(article.id, 50, "budget exhausted: neutral score", boosts))
        except (LLMError, ValidationError) as exc:
            failures.append(f"{article.id}: {type(exc).__name__}")
            scored.append(Scored(article.id, 50, "scoring failed: neutral score", boosts))  # degrade, do not drop
    scored.sort(key=lambda s: -s.final)
    return scored, failures
