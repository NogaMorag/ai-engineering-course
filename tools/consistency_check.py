"""Stage 3 consistency audit over the whole book. Read-only; prints findings grouped by kind.

    uv run --no-project python tools/consistency_check.py

Checks: every TOC chapter file exists and is marked done; every chapter has the fixed apparatus; every fenced block
is wrapped in an LTR div; every relative link resolves; every obsidian note exists and its [[links]] resolve; every
exercise dir referenced by a chapter has README/solution/tests and every exercise README has the template sections; appendix F has
day blocks 0..80; chapter cross-references ("פרק N") point at existing
chapters; day references ("יום N") are within 0..80; schedule day titles vs chapter exercise days; no employer terms.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK, NOTES, EXERCISES = ROOT / "book", ROOT / "obsidian", ROOT / "exercises"
APPARATUS = ["## מה נלמד בפרק", "## ידע מקדים", "## סיכום", "## מונחים לזכור", "## טעויות נפוצות", "## שאלות ראיון", "## פתק Obsidian", "## תרגיל", "## העשרה אופציונלית"]
FORBIDDEN = re.compile(r"drivenets|dnos|nmorag|ACO-workspace|paseo|\bAICO-[0-9]", re.IGNORECASE)


def chapters() -> list[Path]:
    return sorted(BOOK.glob("[0-9][0-9]-*.md"))


def check_toc(findings: list[str]) -> None:
    toc = (BOOK / "README.md").read_text(encoding="utf-8")
    for m in re.finditer(r"\| (פרק \d+|[א-ו]): [^|]+ \| (\[?`([^`]+)`\]?(?:\([^)]+\))?) \| (✅|⏳|🛠) \|", toc):
        label, _, file, status = m.groups()
        path = BOOK / file
        if not path.exists():
            findings.append(f"toc: {label} points at missing {file}")
        elif status != "✅":
            findings.append(f"toc: {label} exists but is marked {status}")


def check_chapters(findings: list[str]) -> None:
    slugs = {p.stem for p in chapters()}
    numbers = {int(p.name[:2]) for p in chapters()}
    for path in chapters():
        text = path.read_text(encoding="utf-8")
        n = int(path.name[:2])
        if n > 0:
            for h in APPARATUS:
                if h not in text:
                    findings.append(f"{path.name}: missing {h}")
        lines = text.splitlines()
        fences = sum(1 for l in lines if l.startswith("```")) // 2
        wraps = sum(1 for l in lines if l.strip() == '<div dir="ltr" align="left">')
        if fences != wraps:
            findings.append(f"{path.name}: {fences} fences but {wraps} ltr wrappers")
        for link in re.findall(r"\]\(((?:\.\./|\./)?[^)#\s]+\.md)\)", text):
            if not (path.parent / link).exists():
                findings.append(f"{path.name}: broken link {link}")
        for ref in {int(x) for x in re.findall(r"פרק (\d+)", text)}:
            if ref not in numbers:
                findings.append(f"{path.name}: refers to chapter {ref} which does not exist")
        for day in {int(x) for x in re.findall(r"יום (\d+)", text)}:
            if not 0 <= day <= 80:
                findings.append(f"{path.name}: day {day} outside 0..80")
        if FORBIDDEN.search(text):
            findings.append(f"{path.name}: forbidden term")
        if n > 0:
            note = NOTES / f"{path.stem}.md"
            if not note.exists():
                findings.append(f"{path.name}: no obsidian note")
            else:
                for target in re.findall(r"\[\[([^\]]+)\]\]", note.read_text(encoding="utf-8")):
                    if target not in slugs:
                        findings.append(f"obsidian/{note.name}: link to missing note {target}")
        for ex in set(re.findall(r"exercises/([a-z0-9-]+)/README\.md", text)):
            folder = EXERCISES / ex
            if not folder.exists():
                findings.append(f"{path.name}: exercise folder {ex} missing")
                continue
            if not (folder / "README.md").exists():
                findings.append(f"{ex}: no README")
            if ex.startswith("ch") and not any((folder / sub).exists() for sub in ("solution", "tests", "cases", "templates", "data")):
                findings.append(f"{ex}: no solution/tests/cases/templates")


def check_schedule_alignment(findings: list[str]) -> None:
    """The **זמן:** line of each exercise names its days; blocks must be in order (a shared boundary day is allowed)."""
    last_end = 0
    for path in chapters():
        n = int(path.name[:2])
        if n < 2:
            continue
        text = path.read_text(encoding="utf-8")
        section = text.split("## תרגיל", 1)[1] if "## תרגיל" in text else ""
        time_line = next((l for l in section.splitlines() if "**זמן:**" in l), "")
        found = [int(d) for pair in re.findall(r"(?:יום|ימים) (\d+)(?: עד (\d+)| ו־(\d+))?", time_line) for d in pair if d]
        if not found:
            continue
        start, end = min(found), max(found)
        if start < last_end and n not in (30, 31, 32):  # the project chapters share the project days
            findings.append(f"{path.name}: exercise days {start}-{end} overlap previous chapters (last end {last_end})")
        last_end = max(last_end, end)


def check_hebrew_schedule(findings: list[str]) -> None:
    """Appendix F must carry one '### יום N' block for every day 0..80, in order."""
    text = (BOOK / "appendices" / "f-daily-schedule.md").read_text(encoding="utf-8")
    days = [int(d) for d in re.findall(r"^### יום (\d+)", text, flags=re.MULTILINE)]
    if days != list(range(0, 81)):
        missing = sorted(set(range(0, 81)) - set(days))
        extra = sorted(set(days) - set(range(0, 81)))
        findings.append(f"appendices/f-daily-schedule.md: day blocks {len(days)} (missing {missing[:5]}, extra {extra[:5]}, in order: {days == sorted(days)})")


EXERCISE_SECTIONS = ["## רשימת בדיקה", "## טעויות נפוצות ותיקונים", "## רמזים", "## הפתרון", "## מה התרגיל מדגים"]
NON_CODING = {"ch27-system-design", "ch28-question-bank", "ch29-portfolio"}


def check_exercise_readmes(findings: list[str]) -> None:
    """Every coding exercise README carries the template sections (goal, time, prerequisites, checklist, mistakes, hints, solution, demonstrates)."""
    for folder in sorted(EXERCISES.glob("ch*/")):
        text = (folder / "README.md").read_text(encoding="utf-8")
        required = ["**מטרה:**", "ידע מקדים", "## מה התרגיל מדגים", "## רשימת בדיקה"]
        if folder.name not in NON_CODING:
            required += EXERCISE_SECTIONS + ["## פלט צפוי"]
        if not re.search(r"\*\*זמן(?: משוער)?:\*\*", text):
            findings.append(f"{folder.name}/README.md: no time estimate")
        for section in required:
            if section not in text:
                findings.append(f"{folder.name}/README.md: missing {section}")


def main() -> int:
    findings: list[str] = []
    check_toc(findings)
    check_chapters(findings)
    check_schedule_alignment(findings)
    check_hebrew_schedule(findings)
    check_exercise_readmes(findings)
    for appendix in sorted((BOOK / "appendices").glob("*.md")):
        text = appendix.read_text(encoding="utf-8")
        lines = text.splitlines()
        if sum(1 for l in lines if l.startswith("```")) // 2 != sum(1 for l in lines if l.strip() == '<div dir="ltr" align="left">'):
            findings.append(f"appendices/{appendix.name}: fence/wrapper mismatch")
        if FORBIDDEN.search(text):
            findings.append(f"appendices/{appendix.name}: forbidden term")
    print(f"{len(chapters())} chapters, {len(list((BOOK / 'appendices').glob('*.md')))} appendices checked")
    for f in findings:
        print("-", f)
    print("OK" if not findings else f"{len(findings)} finding(s)")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
