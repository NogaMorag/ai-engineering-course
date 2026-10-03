r"""Chapter 17 starter: from eval records to a prioritized error analysis, and a regression set.

    uv run python -m ch17.analyze results\dev-v1.jsonl --out results\analysis-v1.md --regressions regressions.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from ch16.cases import CASES_PATH, Case, load_cases
from ch16.harness import read_records
from ch17.taxonomy import TAXONOMY, classify

Record = dict[str, Any]


def tag_records(records: list[Record], cases: list[Case]) -> list[tuple[Record, list[str]]]:
    by_id = {c.id: c for c in cases}
    return [(r, classify(r, by_id[r["case_id"]])) for r in records if r["case_id"] in by_id]


def rollup(tagged: list[tuple[Record, list[str]]]) -> tuple[Counter[str], Counter[str]]:
    by_type: Counter[str] = Counter()
    by_stage: Counter[str] = Counter()
    for _, tags in tagged:
        for tag in tags:
            by_type[tag] += 1
            by_stage[TAXONOMY[tag].stage if tag in TAXONOMY else "unknown"] += 1
    return by_type, by_stage


def prioritize(by_type: Counter[str]) -> list[tuple[str, int, int]]:
    """(failure type, count, priority = count x severity), highest priority first."""
    # TODO 2: priority = count x severity (1 for unknown types); sort by priority, then count, then name.
    raise NotImplementedError


def render_analysis(tagged: list[tuple[Record, list[str]]], title: str) -> str:
    by_type, by_stage = rollup(tagged)
    failures = [(r, t) for r, t in tagged if t]
    lines = [f"# {title}", "", f"{len(failures)} failing cases out of {len(tagged)}.", "", "## By stage", "", "| stage | tags |", "| --- | --- |"]
    for stage in ("ingestion", "retrieval", "context", "generation", "validation", "unknown"):
        if by_stage[stage]:
            lines.append(f"| {stage} | {by_stage[stage]} |")
    lines += ["", "## Priorities (count x severity)", "", "| failure type | count | priority | stage | fix type | what it means |", "| --- | --- | --- | --- | --- | --- |"]
    for name, count, priority in prioritize(by_type):
        f = TAXONOMY.get(name)
        lines.append(f"| {name} | {count} | {priority} | {f.stage if f else '-'} | {f.fix_type if f else '-'} | {f.description if f else 'needs a human look'} |")
    lines += ["", "## Failing cases", ""]
    for r, tags in failures:
        lines.append(f"- **{r['case_id']}** [{r['category']}] {r['question'][:70]} → {', '.join(tags)}")
        lines.append(f"  retrieved: {', '.join(p.split('/')[-1] for p in r.get('retrieved_paths', [])) or '-'} | cited: {', '.join(r.get('cited_paths', [])) or '-'} | abstained: {r['abstained']}")
    lines += ["", "## Suggested order of fixes", ""]
    for name, count, _ in prioritize(by_type)[:3]:
        f = TAXONOMY.get(name)
        if f:
            lines.append(f"1. **{name}** ({count}): a {f.fix_type} fix at the {f.stage} stage. Re-run the dev split and compare before touching anything else.")
    return "\n".join(lines) + "\n"


def regression_cases(tagged: list[tuple[Record, list[str]]], cases: list[Case]) -> list[Case]:
    by_id = {c.id: c for c in cases}
    return [by_id[r["case_id"]] for r, tags in tagged if tags]


def append_regressions(new_cases: list[Case], path: Path) -> int:
    existing = {json.loads(line)["id"] for line in path.read_text(encoding="utf-8").splitlines() if line.strip()} if path.exists() else set()
    added = [c for c in new_cases if c.id not in existing]
    with path.open("a", encoding="utf-8") as handle:
        for case in added:
            handle.write(case.model_dump_json() + "\n")
    return len(added)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tag failing eval records, roll up a taxonomy, prioritize fixes.")
    parser.add_argument("results", type=Path)
    parser.add_argument("--cases", type=Path, default=CASES_PATH)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--regressions", type=Path, help="append failing cases to this JSONL regression set")
    args = parser.parse_args(argv)
    cases = load_cases(args.cases)
    tagged = tag_records(read_records(args.results), cases)
    report = render_analysis(tagged, f"Error analysis: {args.results.stem}")
    if args.out:
        args.out.write_text(report, encoding="utf-8")
    print(report)
    if args.regressions:
        added = append_regressions(regression_cases(tagged, cases), args.regressions)
        print(f"added {added} regression case(s) to {args.regressions}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
