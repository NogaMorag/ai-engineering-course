"""Stage 9: the run report, from the trace file and the stage results. Cost, timing, failures, per stage."""
from __future__ import annotations
from collections import defaultdict
from typing import Any
from morning_brief.tracing import read_spans

def build_report(*, run_id: str, date: str, status: str, stages: list[dict[str, Any]], cost_usd: float, trace_path: str, failures: list[str], cost_by_stage: dict[str, float] | None=None) -> dict[str, Any]:
    raise NotImplementedError

def render_report(report: dict[str, Any]) -> str:
    raise NotImplementedError
