"""Render the chapter-28 question bank section from the JSONL data (single source of truth).

    uv run --no-project python tools/render_question_bank.py

Replaces everything between the markers <!-- bank:start --> and <!-- bank:end --> in book/28-interview-question-bank.md.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "exercises/ch28-question-bank/data/questions.jsonl"
CHAPTER = ROOT / "book/28-interview-question-bank.md"
TITLES = {
    "fundamentals": "יסודות (פרקים 1 עד 6)",
    "apis-prompting": "ממשקים והנחיות (פרקים 7 עד 11)",
    "rag": "אחזור ו־RAG (פרקים 12 עד 15)",
    "evals": "הערכה ובדיקות (פרקים 16 עד 18)",
    "agents": "סוכנים (פרקים 19 עד 21)",
    "production": "פרודקשן (פרקים 22, 23, 25, 26)",
    "security": "אבטחה ופרטיות (פרק 24)",
    "project": "„ספרי לי על הפרויקט שלך” (פרקים 30 עד 32)",
}
PART_ONE = {"fundamentals", "apis-prompting", "rag", "evals"}


def render() -> str:
    rows = [json.loads(line) for line in BANK.read_text(encoding="utf-8").splitlines() if line.strip()]
    out: list[str] = []
    for part, cats in (("### חלק ראשון (יום 73)", [c for c in TITLES if c in PART_ONE]), ("### חלק שני (יום 74)", [c for c in TITLES if c not in PART_ONE])):
        out += [part, ""]
        for cat in cats:
            out += [f"#### {TITLES[cat]}", ""]
            for row in (r for r in rows if r["category"] == cat):
                out.append(f"**{row['id']}. {row['question']}** (פרק {row['chapter']})")
                out.append("")
                out.append(row["answer"])
                if row.get("tradeoff"):
                    out.append("")
                    out.append(f"*שורת הפשרה:* {row['tradeoff']}")
                if row.get("follow_up"):
                    out.append("")
                    out.append(f"**המשך:** {row['follow_up']}")
                out.append("")
    return "\n".join(out).rstrip() + "\n"


def main() -> None:
    text = CHAPTER.read_text(encoding="utf-8")
    start, end = "<!-- bank:start -->", "<!-- bank:end -->"
    a, b = text.index(start) + len(start), text.index(end)
    CHAPTER.write_text(text[:a] + "\n\n" + render() + "\n" + text[b:], encoding="utf-8")
    print("question bank rendered into", CHAPTER.name)


if __name__ == "__main__":
    main()
