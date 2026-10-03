"""Stage 7: from structured inputs to the Newsletter model. Code composes; the model writes two sentences."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ValidationError

from morning_brief.budget import BudgetExceeded, BudgetGuard
from morning_brief.config import Profile
from morning_brief.llm import prompts
from morning_brief.llm.client import LLMClient, LLMError
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
    also_covered: list[dict[str, str]] = Field(default_factory=list)  # [{"source", "url"}]
    follow_up_of: dict[str, Any] | None = None  # {"day", "url", "similarity"}
    research: ResearchNote | None = None


class Issue(BaseModel):
    date: str
    language: str
    greeting_line: str
    theme: str
    top_stories: list[IssueItem]
    more_stories: list[IssueItem]
    skipped_note: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    def all_urls(self) -> set[str]:
        urls: set[str] = set()
        for item in self.top_stories + self.more_stories:
            urls.add(item.url)
            urls.update(c["url"] for c in item.also_covered)
            if item.follow_up_of:
                urls.add(item.follow_up_of["url"])
        return urls


def build_item(article: Article, summary: ArticleSummary, *, score: float, reason: str, members: list[Article], follow_up: FollowUp | None, research: ResearchNote | None) -> IssueItem:
    return IssueItem(
        article_id=article.id, title=article.title, headline=summary.headline, bullets=summary.bullets, why_it_matters=summary.why_it_matters,
        url=article.url, source=article.source, score=round(score, 1), reason=reason,
        also_covered=[{"source": m.source, "url": m.url} for m in members if m.id != article.id],
        follow_up_of={"day": follow_up.seen_day, "url": follow_up.url, "similarity": follow_up.similarity} if follow_up else None,
        research=research,
    )


def write_intro(date: str, profile: Profile, headlines: list[str], client: LLMClient, *, guard: BudgetGuard | None = None, prompt_version: int = 1) -> IssueIntro:
    """The only model call in composition. A failure degrades to a plain greeting; the issue still goes out."""
    system = prompts.render(prompts.load("compose", prompt_version), profile=profile.as_prompt_block(), language=profile.language)
    listed = "\n".join(f"- {h}" for h in headlines) or "- (no top stories today)"
    try:
        completion = client.complete(f"date: {date}\n<headlines>\n{listed}\n</headlines>", system=system, max_output_tokens=200, temperature=0.4, response_format=response_format_for(IssueIntro))
        if guard:
            guard.charge(client.model, input_tokens=completion.input_tokens, output_tokens=completion.output_tokens, cached_tokens=completion.cached_tokens, stage="compose")
        return IssueIntro.model_validate_json(completion.text)
    except (LLMError, ValidationError, BudgetExceeded):
        greeting = "בוקר טוב. הנה העיתון של היום." if profile.language == "he" else "Good morning. Here is today's brief."
        return IssueIntro(greeting_line=f"{greeting} ({date})", theme="none")


def compose_issue(date: str, profile: Profile, top: list[IssueItem], more: list[IssueItem], intro: IssueIntro, *, metadata: dict[str, Any], skipped_note: str = "") -> Issue:
    return Issue(date=date, language=profile.language, greeting_line=intro.greeting_line, theme=intro.theme, top_stories=top, more_stories=more, skipped_note=skipped_note, metadata=metadata)
