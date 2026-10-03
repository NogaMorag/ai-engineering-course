r"""Chapter 25 solution: the job that runs without you. Produces one artifact per day and a run report.

    uv run --env-file .env python -m ch25.daily_job --out out                 # real model
    uv run python -m ch25.daily_job --out out --dry-run                       # fake model, for CI and tests
    uv run python -m ch25.daily_job --out out --local-hour 7                  # exit 0 without work if it is not 07:00 in Jerusalem

Exit codes: 0 ok, 2 skipped (wrong hour), 3 the model failed, 4 budget exceeded,
5 versions.json disagrees with the environment or a declared prompt file is missing (nothing ran).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from ch09.schemas import RESPONSE_FORMAT, ArticleSummary
from ch09.summarize_structured import SYSTEM, build_prompt
from ch11.llm_client import FakeClient, GeminiClient, LLMClient, LLMError
from ch19.research_tools import load_feeds
from ch22.tracing import Tracer, TracingClient
from ch23.budget import BudgetExceeded, BudgetGuard
from ch25.schedule_math import is_local_hour
from ch25.versions import check_versions, load_versions

EXIT_OK, EXIT_SKIPPED, EXIT_MODEL_FAILED, EXIT_BUDGET, EXIT_VERSIONS = 0, 2, 3, 4, 5


def fake_client_for_dry_run(n: int) -> FakeClient:
    valid = {"is_article": True, "headline": "Dry run headline", "bullets": ["One.", "Two.", "Three."], "why_it_matters": "Why it matters: dry run.", "tags": ["test"], "confidence": "low"}
    return FakeClient(script=[json.dumps(valid)] * n)


def render_brief(day: dt.date, entries: list[tuple[dict, ArticleSummary]]) -> str:
    lines = [f"# Morning brief, {day.isoformat()}", ""]
    for item, summary in entries:
        lines += [f"## {summary.headline}", ""] + [f"- {b}" for b in summary.bullets] + ["", summary.why_it_matters, "", f"_Source: {item['source']}, {item['published']} ({item['id']})_", ""]
    if not entries:
        lines.append("_No articles today._")
    return "\n".join(lines) + "\n"


def run_job(client: LLMClient, *, out_dir: Path, day: dt.date, model: str, items: int, budget_usd: float, tracer: Tracer) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    guard = BudgetGuard(budget_usd)
    traced = TracingClient(client, tracer, model=model, stage="summarize")
    entries, failures = [], 0
    for item in load_feeds()[:items]:
        try:
            completion = traced.complete(build_prompt(item["text"]), system=SYSTEM, max_output_tokens=400, temperature=0.1, response_format=RESPONSE_FORMAT)
            guard.charge(model, completion)
            entries.append((item, ArticleSummary.model_validate_json(completion.text)))
        except BudgetExceeded as exc:
            tracer.event("budget_exceeded", str(exc))
            _write_report(out_dir, day, tracer, guard, entries, failures, "budget_exceeded")
            return EXIT_BUDGET
        except (LLMError, ValidationError) as exc:
            failures += 1
            tracer.event("item_failed", f"{item['id']}: {type(exc).__name__}")
    (out_dir / f"brief-{day.isoformat()}.md").write_text(render_brief(day, entries), encoding="utf-8")
    _write_report(out_dir, day, tracer, guard, entries, failures, "ok" if entries else "no_output")
    return EXIT_OK if entries else EXIT_MODEL_FAILED


def _write_report(out_dir: Path, day: dt.date, tracer: Tracer, guard: BudgetGuard, entries: list, failures: int, status: str) -> None:
    report = {"day": day.isoformat(), "status": status, "items_ok": len(entries), "items_failed": failures, "calls": guard.calls, "spent_usd": round(guard.spent_usd, 6), "trace_file": str(tracer.path)}
    (out_dir / "run-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Daily brief job.")
    parser.add_argument("--out", type=Path, default=Path("out"))
    parser.add_argument("--items", type=int, default=5)
    parser.add_argument("--budget-usd", type=float, default=0.05)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--local-hour", type=int, help="exit 2 unless it is this hour in Asia/Jerusalem (for double-scheduled cron lines)")
    parser.add_argument("--versions", type=Path, default=Path("versions.json"))
    parser.add_argument("--prompts-dir", type=Path, default=Path("ch08/prompts"), help="where the declared prompt version must exist")
    args = parser.parse_args(argv)
    now = dt.datetime.now(tz=dt.UTC)
    if args.local_hour is not None and not is_local_hour(now, args.local_hour):
        print(f"not {args.local_hour:02d}:00 in Jerusalem (it is {now.astimezone(dt.UTC).isoformat()}); skipping", file=sys.stderr)
        return EXIT_SKIPPED
    versions = load_versions(args.versions) if args.versions.exists() else None
    if versions:  # fail early, before any model call: a mismatch is a bug in the deployment, not a strange newsletter
        problems = check_versions(versions, prompts_dir=args.prompts_dir)
        if problems:
            for problem in problems:
                print(f"version mismatch: {problem}", file=sys.stderr)
            return EXIT_VERSIONS
    model = versions.model_fast if versions else "gemini-3.5-flash-lite"
    tracer = Tracer(args.out / "traces.jsonl")
    client = fake_client_for_dry_run(args.items) if args.dry_run else GeminiClient(model)
    return run_job(client, out_dir=args.out, day=now.date(), model=model, items=args.items, budget_usd=args.budget_usd, tracer=tracer)


if __name__ == "__main__":
    sys.exit(main())
