"""Stage 3: structured summaries. One repair attempt, per-article isolation, stored once, traced and budgeted."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from pydantic import ValidationError

from morning_brief.budget import BudgetExceeded, BudgetGuard
from morning_brief.llm import prompts
from morning_brief.llm.client import LLMClient, LLMError
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
    return f"<article>\n<title>{article.title}</title>\n{article.text.strip()}\n</article>"


def summarize_one(article: Article, client: LLMClient, system: str, *, tracer: Tracer | None = None, guard: BudgetGuard | None = None) -> ArticleSummary:
    """Ask, validate, repair once. Raises LLMError / ValidationError on a final failure."""
    prompt = build_prompt(article)
    last_error: Exception | None = None
    for attempt in range(2):
        completion = client.complete(prompt, system=system, max_output_tokens=500, temperature=0.1, response_format=SUMMARY_FORMAT)
        cost = estimate_cost(client.model, completion.input_tokens - completion.cached_tokens, completion.output_tokens, cached_tokens=completion.cached_tokens)
        if tracer:
            tracer.event("summarize.call", article.id, model=client.model, attempt=attempt + 1, input_tokens=completion.input_tokens, output_tokens=completion.output_tokens, cached_tokens=completion.cached_tokens, cost_usd=round(cost, 6))
        if guard:
            guard.charge(client.model, input_tokens=completion.input_tokens, output_tokens=completion.output_tokens, cached_tokens=completion.cached_tokens, stage="summarize")
        try:
            return ArticleSummary.model_validate_json(completion.text)
        except ValidationError as exc:
            last_error = exc
            prompt = f"{build_prompt(article)}\n\nYour previous output was rejected by the validator:\n{exc}\n\nReturn a corrected JSON object only."
    raise last_error  # type: ignore[misc]


def summarize_articles(articles: list[Article], client: LLMClient, store: Store, *, tracer: Tracer | None = None, guard: BudgetGuard | None = None, prompt_version: int = 1, concurrency: int = 3) -> SummaryResult:
    result = SummaryResult()
    system = prompts.load("summarize", prompt_version).body
    todo: list[Article] = []
    for article in articles:
        cached = store.get_summary(article.id)
        if cached:
            result.summaries[article.id] = ArticleSummary.model_validate_json(cached)
            result.reused += 1
        elif article.text.strip():
            todo.append(article)
        else:
            result.failures.append(f"{article.id}: no text")

    def work(article: Article) -> tuple[str, ArticleSummary | None, str | None]:
        try:
            return article.id, summarize_one(article, client, system, tracer=tracer, guard=guard), None
        except BudgetExceeded as exc:
            return article.id, None, f"budget: {exc}"
        except (LLMError, ValidationError) as exc:
            return article.id, None, f"{type(exc).__name__}: {str(exc)[:120]}"

    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        for article_id, summary, error in pool.map(work, todo):
            if summary is not None:
                result.summaries[article_id] = summary
                store.save_summary(article_id, summary.model_dump_json(), model=client.model, tokens_in=0, tokens_out=0, cost=0.0)
            else:
                result.failures.append(f"{article_id}: {error}")
                if error and error.startswith("budget"):
                    result.budget_stopped = True
    return result
