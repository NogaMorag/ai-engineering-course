"""Chapter 19 starter: two workflow patterns in code. Routing picks a prompt; parallelization bounds concurrency.

Workflows decide the control flow in code; the model fills in the steps. No autonomy is involved yet.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable, Iterable
from typing import Any, Literal

from pydantic import BaseModel, Field

from ch09.schemas import clean_schema
from ch11.llm_client import LLMClient

# ---------------------------------------------------------------- routing

Kind = Literal["release_notes", "incident_postmortem", "research_result", "business_news", "other"]


class Route(BaseModel):
    kind: Kind = Field(description="The type of article. 'other' when none fits.")


ROUTE_FORMAT: dict[str, Any] = {"type": "text", "mime_type": "application/json", "schema": clean_schema(Route.model_json_schema())}
ROUTER_SYSTEM = "Classify the article inside <article> tags into exactly one kind. Judge only from the text."

PROMPT_BY_KIND: dict[str, str] = {
    "release_notes": "Summarize this release for an engineer deciding whether to upgrade: what changed, what breaks, what to do before upgrading. Three bullets.",
    "incident_postmortem": "Summarize this postmortem: trigger, impact, root cause, and the fixes. Three bullets, each one sentence.",
    "research_result": "Summarize this research result: the claim, the evidence, and the stated caveats. Three bullets.",
    "business_news": "Summarize this business news: who, what happened, and what it means for customers. Three bullets.",
    "other": "Summarize this text in three one-sentence bullets.",
}


def route(client: LLMClient, article: str) -> str:
    completion = client.complete(f"<article>\n{article}\n</article>", system=ROUTER_SYSTEM, max_output_tokens=50, temperature=0.0, response_format=ROUTE_FORMAT)
    return Route.model_validate_json(completion.text).kind


def summarize_routed(client: LLMClient, article: str) -> tuple[str, str]:
    """Route first, then summarize with the prompt chosen for that kind. Returns (kind, summary)."""
    kind = route(client, article)
    completion = client.complete(f"<article>\n{article}\n</article>", system=PROMPT_BY_KIND[kind], max_output_tokens=300, temperature=0.2)
    return kind, completion.text.strip()


# ---------------------------------------------------------------- parallelization


async def parallel_map[T, R](fn: Callable[[T], R], items: Iterable[T], *, concurrency: int) -> list[R]:
    """Run a blocking function over items with at most `concurrency` in flight. Order is preserved."""
    # TODO 1: an asyncio.Semaphore(concurrency); an inner coroutine that acquires it and runs
    # asyncio.to_thread(fn, item); asyncio.gather over all items (gather preserves order).
    raise NotImplementedError


def run_parallel[T, R](fn: Callable[[T], R], items: Iterable[T], *, concurrency: int = 3) -> list[R]:
    return asyncio.run(parallel_map(fn, list(items), concurrency=concurrency))


def timed[R](fn: Callable[[], R]) -> tuple[R, float]:
    started = time.monotonic()
    result = fn()
    return result, time.monotonic() - started
