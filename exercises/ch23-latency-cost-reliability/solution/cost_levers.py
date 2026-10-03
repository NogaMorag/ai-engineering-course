"""Chapter 23 solution, day 45: cut the cost of summarizing 50 items by half, with the eval score next to it.

    uv run --env-file .env python -m ch23.cost_levers --items 50
    uv run --env-file .env python -m ch23.cost_levers --items 50 --batch     # also submits the non-urgent half as a batch job

Levers, in the order they are applied: 1 model tiering, 2 prompt caching (stable prefix), 3 shorter outputs,
4 the Batch API for whatever can wait. The "eval" is the deterministic validity check from chapter 9.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass

from pydantic import ValidationError

from ch09.schemas import RESPONSE_FORMAT, ArticleSummary
from ch09.summarize_structured import SYSTEM, build_prompt
from ch11.llm_client import GeminiClient, LLMClient
from ch19.research_tools import load_feeds
from ch22.tracing import estimate_cost
from ch23.budget import BudgetGuard

SHORT_SYSTEM = SYSTEM + "\nKeep every bullet under 15 words and the headline under 8 words."


@dataclass
class Variant:
    name: str
    model: str
    system: str
    max_output_tokens: int


@dataclass
class VariantResult:
    name: str
    model: str
    items: int
    valid: int
    input_tokens: int
    cached_tokens: int
    output_tokens: int
    seconds: float
    cost_usd: float

    def row(self) -> dict[str, object]:
        return {
            "variant": self.name, "model": self.model, "valid": f"{self.valid}/{self.items}",
            "in_tokens": self.input_tokens, "cached": self.cached_tokens, "out_tokens": self.output_tokens,
            "seconds": round(self.seconds, 1), "cost_usd": round(self.cost_usd, 5),
        }


def run_variant(client: LLMClient, variant: Variant, articles: list[str], guard: BudgetGuard | None = None) -> VariantResult:
    result = VariantResult(variant.name, variant.model, len(articles), 0, 0, 0, 0, 0.0, 0.0)
    started = time.monotonic()
    for article in articles:
        completion = client.complete(build_prompt(article), system=variant.system, max_output_tokens=variant.max_output_tokens, temperature=0.1, response_format=RESPONSE_FORMAT)
        result.input_tokens += completion.input_tokens
        result.cached_tokens += completion.cached_tokens
        result.output_tokens += completion.output_tokens
        try:
            ArticleSummary.model_validate_json(completion.text)
            result.valid += 1
        except ValidationError:
            pass
        if guard:
            guard.charge(variant.model, completion)
    result.seconds = time.monotonic() - started
    result.cost_usd = estimate_cost(variant.model, result.input_tokens - result.cached_tokens, result.output_tokens, cached_tokens=result.cached_tokens)
    return result


def render(results: list[VariantResult]) -> str:
    rows = [r.row() for r in results]
    headers = list(rows[0])
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    out += ["| " + " | ".join(str(r[h]) for h in headers) + " |" for r in rows]
    if len(results) >= 2 and results[0].cost_usd:
        saving = 1 - results[-1].cost_usd / results[0].cost_usd
        out.append(f"\nlast variant vs first: {saving:.0%} cheaper; validity {results[0].valid}/{results[0].items} -> {results[-1].valid}/{results[-1].items}")
    return "\n".join(out)


def submit_batch(model: str, articles: list[str]) -> str:
    """The non-urgent half as a batch job (50 percent price, hours of latency). Returns the job name to poll."""
    from google import genai
    from google.genai import types

    client = genai.Client()
    requests = [types.InlinedRequest(contents=build_prompt(a), config=types.GenerateContentConfig(system_instruction=SHORT_SYSTEM, max_output_tokens=300)) for a in articles]
    job = client.batches.create(model=model, src=requests, config=types.CreateBatchJobConfig(display_name="ch23-non-urgent-half"))
    return job.name or ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=int, default=50)
    parser.add_argument("--batch", action="store_true")
    parser.add_argument("--budget-usd", type=float, default=0.50)
    args = parser.parse_args()
    fast, smart = os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite"), os.environ.get("MODEL_SMART", "gemini-3.8-flash")
    feeds = load_feeds()
    articles = [feeds[i % len(feeds)]["text"] for i in range(args.items)]
    guard = BudgetGuard(args.budget_usd)
    variants = [
        Variant("baseline: smart, long", smart, SYSTEM, 600),
        Variant("lever 1: fast model", fast, SYSTEM, 600),
        Variant("lever 1+3: fast, short output", fast, SHORT_SYSTEM, 250),
    ]
    results = [run_variant(GeminiClient(v.model), v, articles, guard) for v in variants]
    print(render(results))
    print(f"\nbudget: spent {guard.spent_usd:.4f} of {guard.max_usd:.2f} USD over {guard.calls} calls")
    print("lever 2 (prompt caching) shows up in the 'cached' column once the shared prefix is long enough for the model.")
    if args.batch:
        name = submit_batch(fast, articles[len(articles) // 2 :])
        print(f"lever 4: submitted the non-urgent half as batch job {name}; poll with client.batches.get(name=...)")
        print(json.dumps({"job": name, "items": len(articles) // 2}))


if __name__ == "__main__":
    main()
