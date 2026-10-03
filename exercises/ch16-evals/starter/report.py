"""Chapter 16 starter: per-category numerators and denominators, cost, and a comparison of two runs."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

Record = dict[str, Any]


def _rate(numerator: int, denominator: int) -> str:
    return f"{numerator}/{denominator}" if denominator else "-"


def summarize(records: list[Record]) -> dict[str, dict[str, Any]]:
    by_category: dict[str, list[Record]] = defaultdict(list)
    for r in records:
        by_category[r["category"]].append(r)
    by_category["ALL"] = list(records)
    summary: dict[str, dict[str, Any]] = {}
    for category, rows in by_category.items():
        checks = [c for r in rows for c in r["checks"]]
        judged = [r["judge"] for r in rows if r.get("judge")]
        summary[category] = {
            "n": len(rows),
            "passed": sum(1 for r in rows if r["passed"]),
            "abstention_ok": sum(1 for c in checks if c["name"] == "abstention" and c["passed"]),
            "abstention_n": sum(1 for c in checks if c["name"] == "abstention"),
            "citations_ok": sum(1 for c in checks if c["name"] == "has_citation" and c["passed"]),
            "citations_n": sum(1 for c in checks if c["name"] == "has_citation"),
            "flaky": sum(1 for r in rows if r.get("flaky")),
            "judged": len(judged),
            "faithful": sum(1 for j in judged if j["faithful"]),
            "correctness_mean": round(sum(j["correctness"] for j in judged) / len(judged), 2) if judged else None,
            "input_tokens": sum(r.get("input_tokens", 0) for r in rows),
            "output_tokens": sum(r.get("output_tokens", 0) for r in rows),
        }
    return summary


def render_markdown(records: list[Record], title: str) -> str:
    summary = summarize(records)
    lines = [f"# {title}", "", "| category | passed | abstention ok | has citation | faithful (judge) | correctness | flaky |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for category, s in summary.items():
        lines.append(
            f"| {category} | {_rate(s['passed'], s['n'])} | {_rate(s['abstention_ok'], s['abstention_n'])} | "
            f"{_rate(s['citations_ok'], s['citations_n'])} | {_rate(s['faithful'], s['judged'])} | "
            f"{s['correctness_mean'] if s['correctness_mean'] is not None else '-'} | {s['flaky']} |"
        )
    total = summary["ALL"]
    lines += ["", f"Cost of this run: {total['input_tokens']} input tokens, {total['output_tokens']} output tokens, {total['n']} cases.", ""]
    failures = [r for r in records if not r["passed"]]
    if failures:
        lines += ["## Failing cases", ""]
        for r in failures:
            failed = ", ".join(f"{c['name']} ({c['detail']})" for c in r["checks"] if not c["passed"])
            lines.append(f"- **{r['case_id']}** [{r['category']}] {r['question'][:70]} — {failed}")
    return "\n".join(lines) + "\n"


def compare(records_a: list[Record], records_b: list[Record], label_a: str = "A", label_b: str = "B") -> str:
    """Per-category deltas and the cases that flipped. Both runs must cover the same case ids."""
    a_by_id = {r["case_id"]: r for r in records_a}
    b_by_id = {r["case_id"]: r for r in records_b}
    shared = sorted(set(a_by_id) & set(b_by_id))
    sa, sb = summarize([a_by_id[i] for i in shared]), summarize([b_by_id[i] for i in shared])
    lines = [f"# {label_a} vs {label_b} ({len(shared)} shared cases)", "", f"| category | {label_a} passed | {label_b} passed | delta |", "| --- | --- | --- | --- |"]
    for category in sa:
        delta = sb[category]["passed"] - sa[category]["passed"]
        lines.append(f"| {category} | {_rate(sa[category]['passed'], sa[category]['n'])} | {_rate(sb[category]['passed'], sb[category]['n'])} | {delta:+d} |")
    fixed = [i for i in shared if not a_by_id[i]["passed"] and b_by_id[i]["passed"]]
    broken = [i for i in shared if a_by_id[i]["passed"] and not b_by_id[i]["passed"]]
    lines += ["", f"Fixed by {label_b}: {', '.join(fixed) or 'none'}", f"Broken by {label_b}: {', '.join(broken) or 'none'}", ""]
    lines.append(f"Tokens: {label_a} {sa['ALL']['input_tokens']}+{sa['ALL']['output_tokens']}, {label_b} {sb['ALL']['input_tokens']}+{sb['ALL']['output_tokens']}.")
    return "\n".join(lines) + "\n"
