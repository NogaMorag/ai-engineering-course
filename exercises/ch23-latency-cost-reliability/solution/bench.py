"""Chapter 23 solution, day 44: a latency benchmark you can defend.

    uv run --env-file .env python -m ch23.bench --runs 10

p50 is the typical call; p95 is what one user in twenty sees; TTFT (time to first token) is what a
person watching a stream feels. Ten runs show the shape, not the truth: say so in the conclusion.
"""

from __future__ import annotations

import argparse
import math
import os
import time
from dataclasses import dataclass

from ch11.llm_client import GeminiClient, LLMClient
from ch22.tracing import estimate_cost

PROMPT = (
    "<article>\nCargo-Lite 2.0 was released on Tuesday with a shared build cache keyed by content hash. One company "
    "reported clean builds dropping from 41 to 6 minutes. The old configuration format is removed in 3.0.\n</article>\n"
    "Summarize in three bullets."
)


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile (p in 0..100) over a non-empty list."""
    if not values:
        raise ValueError("no values")
    ordered = sorted(values)
    rank = max(1, math.ceil(p / 100 * len(ordered)))
    return ordered[rank - 1]


@dataclass
class BenchResult:
    model: str
    runs: int
    total_s: list[float]
    ttft_s: list[float]
    input_tokens: int
    output_tokens: int

    def row(self) -> dict[str, float | str | int]:
        return {
            "model": self.model,
            "runs": self.runs,
            "p50_s": round(percentile(self.total_s, 50), 2),
            "p95_s": round(percentile(self.total_s, 95), 2),
            "ttft_p50_s": round(percentile(self.ttft_s, 50), 2) if self.ttft_s else float("nan"),
            "cost_per_call_usd": round(estimate_cost(self.model, self.input_tokens / self.runs, self.output_tokens / self.runs), 6),
        }


def bench_model(client: LLMClient, model: str, runs: int, *, stream_runs: int = 3, pause_s: float = 0.5) -> BenchResult:
    totals, ttfts, in_tok, out_tok = [], [], 0, 0
    for _ in range(runs):
        started = time.monotonic()
        completion = client.complete(PROMPT, max_output_tokens=200, temperature=0.2)
        totals.append(time.monotonic() - started)
        in_tok += completion.input_tokens
        out_tok += completion.output_tokens
        time.sleep(pause_s)
    for _ in range(stream_runs):
        started = time.monotonic()
        first = None
        for _chunk in client.stream(PROMPT, max_output_tokens=200):
            if first is None:
                first = time.monotonic() - started
        ttfts.append(first or 0.0)
        time.sleep(pause_s)
    return BenchResult(model, runs, totals, ttfts, in_tok, out_tok)


def render_table(rows: list[dict[str, float | str | int]]) -> str:
    headers = list(rows[0])
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines += ["| " + " | ".join(str(r[h]) for h in headers) + " |" for r in rows]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--models", nargs="*", default=[os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite"), os.environ.get("MODEL_SMART", "gemini-3.8-flash")])
    args = parser.parse_args()
    rows = [bench_model(GeminiClient(model), model, args.runs).row() for model in args.models]
    print(render_table(rows))
    print("\nTen runs show the shape of the distribution, not its truth. Repeat at another hour before concluding.")


if __name__ == "__main__":
    main()
