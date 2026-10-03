r"""Command line.

    morning-brief run [--date YYYY-MM-DD] [--resume] [--channels file,email] [--offline] [--stop-after stage]
    morning-brief preview [--date YYYY-MM-DD]
    morning-brief report [--date YYYY-MM-DD]

Exit codes: 0 ok, 2 partial (the issue went out with a note), 3 failed,
5 versions.json disagrees with the environment or a declared prompt file is missing (nothing ran).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from morning_brief.config import Settings, load_profile
from morning_brief.llm.prompts import PROMPTS_DIR
from morning_brief.pipeline import STAGES, Clients, Pipeline
from morning_brief.store import Store


def real_clients(settings: Settings) -> Clients:
    import httpx

    from morning_brief.embeddings import CachedEmbedder, GeminiEmbedder
    from morning_brief.llm.client import GeminiClient
    from morning_brief.research import GeminiAgentBackend

    return Clients(
        fast=GeminiClient(settings.model_fast), smart=GeminiClient(settings.model_smart),
        embedder=CachedEmbedder(GeminiEmbedder(settings.embedding_model), settings.data_dir / "embeddings-cache.sqlite"),
        agent_backend=GeminiAgentBackend(settings.model_smart), http=httpx.Client(),
    )


def load_versions(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def check_versions(versions: dict, settings: Settings, prompts_dir: Path = PROMPTS_DIR) -> list[str]:
    """Mismatches between versions.json and what this run would actually use. Empty list = consistent."""
    problems = []
    for key, actual in (("model_fast", settings.model_fast), ("model_smart", settings.model_smart), ("embedding_model", settings.embedding_model)):
        declared = versions.get(key)
        if declared and declared != actual:
            problems.append(f"{key}: versions.json says {declared}, the environment says {actual}")
    for key in ("prompt_version", "score_prompt_version"):
        declared = versions.get(key)
        if declared and not (prompts_dir / f"{declared}.txt").exists():
            problems.append(f"{key}: prompt file {declared}.txt not found in {prompts_dir}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="morning-brief", description="A scheduled, personalized morning newsletter agent.")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--date", default=dt.datetime.now(tz=dt.UTC).date().isoformat())
    run.add_argument("--resume", action="store_true", help="skip stages whose artifact already exists")
    run.add_argument("--channels", default="file", help="comma-separated: file,email")
    run.add_argument("--offline", action="store_true", help="fixture feeds and fake models; no key, no network")
    run.add_argument("--stop-after", choices=STAGES)
    run.add_argument("--profile", type=Path, default=Path("profile.yaml"))
    run.add_argument("--versions", type=Path, default=Path("versions.json"))
    run.add_argument("--data-dir", type=Path)
    run.add_argument("--out", type=Path)
    for name in ("preview", "report"):
        p = sub.add_parser(name)
        p.add_argument("--date", default=dt.datetime.now(tz=dt.UTC).date().isoformat())
        p.add_argument("--data-dir", type=Path)
    args = parser.parse_args(argv)

    settings = Settings()
    if getattr(args, "data_dir", None):
        settings.data_dir = args.data_dir
    if getattr(args, "out", None):
        settings.out_dir = args.out

    if args.command == "run":
        versions = load_versions(args.versions)
        problems = check_versions(versions, settings)
        if problems:  # fail before any model call: a mismatch is a deployment bug, not a strange issue
            for problem in problems:
                print(f"version mismatch: {problem}", file=sys.stderr)
            return 5
        profile = load_profile(args.profile)
        if args.offline:
            from morning_brief.offline import offline_clients

            clients = offline_clients()
        else:
            clients = real_clients(settings)
        pipeline = Pipeline(settings, profile, clients, versions=versions or None)
        report = pipeline.run(args.date, resume=args.resume, channels=tuple(c.strip() for c in args.channels.split(",") if c.strip()), stop_after=args.stop_after)
        print(f"{report['status']}: cost {report['cost_usd']:.4f} USD, {report['duration_s']} s, {len(report['failures'])} failure(s); report in {settings.data_dir / 'runs' / args.date}")
        return {"ok": 0, "partial": 2}.get(report["status"], 3)

    store = Store(settings.data_dir / "brief.sqlite")
    if args.command == "preview":
        issue = store.get_issue(f"run-{args.date}")
        if not issue:
            print(f"no issue for {args.date}", file=sys.stderr)
            return 3
        print(issue["markdown"])
        return 0
    run_row = store.get_run(f"run-{args.date}")
    if not run_row:
        print(f"no run for {args.date}", file=sys.stderr)
        return 3
    report_path = settings.data_dir / "runs" / args.date / "run-report.md"
    print(report_path.read_text(encoding="utf-8") if report_path.exists() else json.dumps(run_row, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
