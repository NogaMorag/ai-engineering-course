r"""Chapter 22 starter: a run report from a trace file. Per stage: calls, tokens, cost, latency p50/p95, errors.

    uv run python -m ch22.report out\traces.jsonl
"""

from __future__ import annotations

import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from ch22.tracing import PRICES, read_spans


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    return ordered[max(1, math.ceil(p / 100 * len(ordered))) - 1]


def summarize(spans: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    # TODO 3: group llm/tool/stage spans by f"{kind}:{name}"; for each group compute calls, errors, token sums
    # (input, output, cached), cost_usd, p50/p95 of duration_ms (None when no durations), and the sorted set of
    # models that are not in PRICES. Return the dict, sorted by key.
    raise NotImplementedError


def render(spans: list[dict[str, Any]], title: str = "run report") -> str:
    summary = summarize(spans)
    traces = {s["trace_id"] for s in spans}
    lines = [f"# {title}", "", f"{len(spans)} spans, {len(traces)} trace(s).", "", "| span | calls | errors | in | cached | out | cost USD | p50 ms | p95 ms |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    total_cost = 0.0
    for key, s in summary.items():
        total_cost += s["cost_usd"]
        lines.append(f"| {key} | {s['calls']} | {s['errors']} | {s['input_tokens']} | {s['cached_tokens']} | {s['output_tokens']} | {s['cost_usd']:.6f} | {s['p50_ms'] if s['p50_ms'] is not None else '-'} | {s['p95_ms'] if s['p95_ms'] is not None else '-'} |")
    lines += ["", f"Estimated paid-tier cost of this run: {total_cost:.6f} USD."]
    unpriced = sorted({m for s in summary.values() for m in s["unpriced_models"]})
    if unpriced:
        lines.append(f"No price known for: {', '.join(unpriced)} (cost shown as 0; add them to PRICES).")
    events = [s for s in spans if s.get("kind") == "event"]
    if events:
        lines += ["", "## Events", ""] + [f"- {e['name']}: {e.get('detail', '')}" for e in events]
    errors = [s for s in spans if s.get("status") == "error"]
    if errors:
        lines += ["", "## Errors", ""] + [f"- {e['kind']}:{e['name']} — {e.get('error', '')}" for e in errors]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    path = Path((argv or sys.argv[1:] or ["out/traces.jsonl"])[0])
    print(render(read_spans(path), f"run report: {path}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
