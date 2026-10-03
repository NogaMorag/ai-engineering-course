"""Offline tests for chapter 25. Copy to ai-course/tests/test_ch25.py and run: uv run pytest -q"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from ch22.tracing import Tracer
from ch25.daily_job import (
    EXIT_BUDGET,
    EXIT_OK,
    EXIT_SKIPPED,
    EXIT_VERSIONS,
    fake_client_for_dry_run,
    main,
    run_job,
)
from ch25.schedule_math import cron_for_local_time, is_local_hour, utc_hour_for
from ch25.versions import Versions, check_versions, load_versions, write_default


def test_cron_math_handles_both_dst_regimes() -> None:
    assert utc_hour_for(7, 0, dt.date(2026, 7, 15)) == (4, 0)  # IDT, UTC+3
    assert utc_hour_for(7, 0, dt.date(2026, 1, 15)) == (5, 0)  # IST, UTC+2
    plan = cron_for_local_time(7, 0, year=2026)
    assert plan.summer_cron == "0 4 * * *" and plan.winter_cron == "0 5 * * *" and "DST" in plan.note
    assert is_local_hour(dt.datetime(2026, 7, 15, 4, 10, tzinfo=dt.UTC), 7) and not is_local_hour(dt.datetime(2026, 7, 15, 5, 10, tzinfo=dt.UTC), 7)
    assert is_local_hour(dt.datetime(2026, 1, 15, 5, 10, tzinfo=dt.UTC), 7)
    assert cron_for_local_time(9, 30, tz=ZoneInfo("UTC"), year=2026).summer_cron == "30 9 * * *"


def test_versions_file_and_checks(tmp_path: Path) -> None:
    path = tmp_path / "versions.json"
    write_default(path)
    versions = load_versions(path)
    assert versions.prompt_version == "summarize.v3" and versions.schema_version == 1
    prompts = tmp_path / "prompts"
    prompts.mkdir()
    problems = check_versions(versions, prompts_dir=prompts, env={"MODEL_FAST": "gemini-9-ultra"}, index_metadata={"embedding_model": "other-embedder", "index_version": "notes-2026-10"})
    assert len(problems) == 3 and any("summarize.v3.txt" in p for p in problems) and any("MODEL_FAST" in p for p in problems) and any("other-embedder" in p for p in problems)
    (prompts / "summarize.v3.txt").write_text("x", encoding="utf-8")
    assert check_versions(versions, prompts_dir=prompts, env={}, index_metadata={"embedding_model": "gemini-embedding-2"}) == []
    assert Versions.model_validate({**versions.model_dump(), "prompt_version": "summarize.v4"}).prompt_version == "summarize.v4"


def test_daily_job_writes_the_artifact_and_report(tmp_path: Path) -> None:
    out = tmp_path / "out"
    tracer = Tracer(out / "traces.jsonl")
    code = run_job(fake_client_for_dry_run(3), out_dir=out, day=dt.date(2026, 10, 3), model="gemini-3.5-flash-lite", items=3, budget_usd=1.0, tracer=tracer)
    assert code == EXIT_OK
    brief = (out / "brief-2026-10-03.md").read_text(encoding="utf-8")
    assert brief.startswith("# Morning brief, 2026-10-03") and brief.count("## ") == 3
    report = json.loads((out / "run-report.json").read_text(encoding="utf-8"))
    assert report["status"] == "ok" and report["items_ok"] == 3 and report["calls"] == 3
    spans = [json.loads(l) for l in (out / "traces.jsonl").read_text(encoding="utf-8").splitlines()]
    assert sum(1 for s in spans if s.get("kind") == "llm") == 3

    starved = run_job(fake_client_for_dry_run(3), out_dir=tmp_path / "out2", day=dt.date(2026, 10, 3), model="gemini-3.5-flash-lite", items=3, budget_usd=0.0, tracer=Tracer(tmp_path / "out2" / "t.jsonl"))
    assert starved == EXIT_BUDGET and json.loads((tmp_path / "out2" / "run-report.json").read_text(encoding="utf-8"))["status"] == "budget_exceeded"


def test_daily_job_cli_dry_run_and_hour_skip(tmp_path: Path) -> None:
    assert main(["--out", str(tmp_path / "o"), "--dry-run", "--items", "2", "--versions", str(tmp_path / "none.json")]) == EXIT_OK
    assert (tmp_path / "o" / "run-report.json").exists()
    now_local_hour = dt.datetime.now(tz=ZoneInfo("Asia/Jerusalem")).hour
    wrong_hour = (now_local_hour + 12) % 24
    assert main(["--out", str(tmp_path / "o2"), "--dry-run", "--local-hour", str(wrong_hour), "--versions", str(tmp_path / "none.json")]) == EXIT_SKIPPED


def test_daily_job_refuses_a_version_mismatch_before_any_call(tmp_path: Path, monkeypatch) -> None:
    prompts = tmp_path / "prompts"
    prompts.mkdir()
    (prompts / "summarize.v3.txt").write_text("v3", encoding="utf-8")
    write_default(tmp_path / "versions.json")
    args = ["--out", str(tmp_path / "o"), "--dry-run", "--items", "1", "--versions", str(tmp_path / "versions.json"), "--prompts-dir", str(prompts)]
    monkeypatch.setenv("MODEL_FAST", "gemini-9-ultra")
    assert main(args) == EXIT_VERSIONS
    assert not (tmp_path / "o" / "run-report.json").exists()  # nothing ran
    monkeypatch.delenv("MODEL_FAST")
    monkeypatch.delenv("MODEL_SMART", raising=False)
    assert main(args) == EXIT_OK
