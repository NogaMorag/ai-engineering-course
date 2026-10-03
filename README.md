# AI Engineering Course — textbook + study program (Hebrew)

**Status (2026-10-03): complete and self-reviewed.** 33 Hebrew chapters (0–32) in nine parts, six appendices,
33 Obsidian notes, 27 exercise packages plus three career folders, an 80-day schedule (plus a Day 0 for installations),
and the Morning Brief capstone (reference implementation + generated starter). The master table of contents with
per-chapter status is `book/README.md`; the review records are `00-stage1/08-stage3-consistency-review.md` (consistency
review and the self-review change log) and `00-stage1/07-decisions-2026-10-03.md` (every decision and correction, dated).

This repository is personal study material, separate from any work project: nothing here may contain employer code,
names or data.

## Start here

1. Read `book/00-how-to-study.md` (chapter 0), then do **Day 0**: chapter 2 §2.1–2.4, installations only.
2. Follow the daily plan in `book/appendices/f-daily-schedule.md` (Hebrew; the English twin with the same content is
   `00-stage1/03-daily-schedule.md`).
3. Every chapter ends with the same apparatus: summary, terms, misconceptions, interview questions, an Obsidian note,
   the exercise and optional enrichment. Exercises live in `exercises/chNN-<slug>/` with `README.md`, `starter/`,
   `solution/` and `tests/`.

**Platform.** Commands are PowerShell on Windows 11 (the decision taken in Stage 1). Mac users follow the same days with
the equivalents table in chapter 2 §2.13 and the Mac rows at the end of appendix B.

**Model API.** Google Gemini on the free tier (no credit card). Model names live in `.env`, never in code; prices in
appendix C were checked on 2026-10-03.

## Reading the book

The Markdown is written right-to-left with every code block forced left-to-right (`book/CONVENTIONS.md`). The
comfortable way to read is the generated HTML; run from this folder (not from the exercises project):

```bash
uv run --with markdown tools/build_html.py     # writes site/*.html + site/index.html
```

Or open `book/` in Obsidian with the "RTL Support" plugin and the CSS snippet in `obsidian/snippets/`.

## Layout

```text
book/README.md              master table of contents + status
book/CONVENTIONS.md         formatting and writing rules (RTL, terminology, apparatus)
book/NN-<slug>.md           chapters 00..32
book/appendices/            a glossary (generated), b troubleshooting, c costs, d note templates, e checklists, f schedule
exercises/chNN-<slug>/      README (goal, time, steps, expected output, checklist, mistakes, hints, solution), starter/, solution/, tests/
exercises/project-morning-brief/
  README.md                 the capstone brief in Hebrew
  morning-brief/            reference implementation (uv project: src/, tests/, evals/, docs/, .github/workflows/)
  morning-brief-starter/    generated from the reference: function bodies replaced by NotImplementedError, tests kept
obsidian/                   one note per chapter (generated from each chapter's "פתק Obsidian" section) + CSS snippet
tools/                      generators and checks (see below)
00-stage1/                  the plan, decisions, schedule (EN) and review records
site/                       generated HTML
```

## Tools (single sources of truth)

| Command (from this folder) | What it regenerates |
| --- | --- |
| `uv run --no-project python tools/notes_from_chapters.py 1 2 ... 32` | `obsidian/NN-*.md` from the chapters' note sections |
| `uv run --no-project python tools/make_glossary.py` | appendix A from every chapter's terms table |
| `uv run --no-project python tools/render_question_bank.py` | the chapter 28 bank from `exercises/ch28-question-bank/data/questions.jsonl` |
| `uv run --no-project python tools/make_project_starter.py` | `morning-brief-starter/` from `morning-brief/` |
| `uv run --no-project python tools/wrap_ltr_blocks.py` | adds missing LTR wrappers around code fences (idempotent) |
| `uv run --with markdown tools/build_html.py` | `site/` |
| `uv run --no-project python tools/consistency_check.py` | read-only audit: TOC, apparatus, wrappers, links, notes, exercise folders, day refs |

## Verifying the code

Chapter exercises are written to be copied into one uv project (`ai-course/`, chapter 2). To run every chapter's tests
at once, create a scratch project, copy each `exercises/chNN-*/solution/` to `chNN/` and each `tests/` file to `tests/`,
then `uv run pytest -q` (the Stage 3 review did exactly this: 168 passed, 2 skipped by design). The capstone runs its own
suite: `cd exercises/project-morning-brief/morning-brief && uv sync && uv run pytest -q` and
`uv run morning-brief run --offline` for an end-to-end run with fixture feeds and fake models.

## Known limitations

- No live API call was made while writing: this machine has no Gemini key. Every call shape was verified against the
  installed SDK (google-genai 2.28.0) and the official documentation on 2026-10-03; the first live runs (chapter 2,
  then the 💲 days) are the first live checks. Appendix B lists the expected error endings.
- Prices, model names, rate limits and GitHub Actions versions are dated facts; the book says "נכון לאוקטובר 2026" and
  keeps them in `.env`, appendix C and the workflow files, not in prose.
- The reference implementation's eval numbers are placeholders to be filled after the first real week.
