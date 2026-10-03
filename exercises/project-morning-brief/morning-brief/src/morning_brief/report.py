"""Stage 9: the run report, from the trace file and the stage results. Cost, timing, failures, per stage."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from morning_brief.tracing import read_spans


def build_report(*, run_id: str, date: str, status: str, stages: list[dict[str, Any]], cost_usd: float, trace_path: str, failures: list[str], cost_by_stage: dict[str, float] | None = None) -> dict[str, Any]:
    spans = read_spans(trace_path)
    llm_events = [s for s in spans if s.get("kind") == "event" and s.get("name", "").endswith(".call")]
    by_stage: dict[str, dict[str, float]] = defaultdict(lambda: {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cached_tokens": 0, "cost_usd": 0.0})
    for e in llm_events:
        stage = e["name"].split(".")[0]
        by_stage[stage]["calls"] += 1
        for key in ("input_tokens", "output_tokens", "cached_tokens", "cost_usd"):
            by_stage[stage][key] += e.get(key, 0) or 0
    return {
        "run_id": run_id, "date": date, "status": status, "cost_usd": round(cost_usd, 6),
        "duration_s": round(sum(s.get("seconds", 0.0) for s in stages), 1),
        "stages": stages, "llm_by_stage": {k: {kk: (round(vv, 6) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in by_stage.items()},
        "cost_by_stage": {k: round(v, 6) for k, v in (cost_by_stage or {}).items()},
        "failures": failures, "trace_file": trace_path,
    }


def render_report(report: dict[str, Any]) -> str:
    lines = [f"# Run {report['run_id']} ({report['date']}): {report['status']}", "", f"cost {report['cost_usd']:.4f} USD · {report['duration_s']} s · {len(report['failures'])} failure(s)", "", "| stage | items in | items out | seconds | failures |", "| --- | --- | --- | --- | --- |"]
    for s in report["stages"]:
        lines.append(f"| {s['name']} | {s.get('items_in', '-')} | {s.get('items_out', '-')} | {s.get('seconds', 0):.1f} | {s.get('failures', 0)} |")
    if report.get("cost_by_stage"):
        lines += ["", "| stage | cost USD |", "| --- | --- |"] + [f"| {k} | {v:.6f} |" for k, v in report["cost_by_stage"].items()]
    if report["llm_by_stage"]:
        lines += ["", "| llm stage | calls | in | cached | out | cost USD |", "| --- | --- | --- | --- | --- | --- |"]
        for name, v in report["llm_by_stage"].items():
            lines.append(f"| {name} | {int(v['calls'])} | {int(v['input_tokens'])} | {int(v['cached_tokens'])} | {int(v['output_tokens'])} | {v['cost_usd']:.6f} |")
    if report["failures"]:
        lines += ["", "## Failures", ""] + [f"- {f}" for f in report["failures"][:30]]
    return "\n".join(lines) + "\n"
