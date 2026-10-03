# AI Engineering Course — textbook + study program (Hebrew)

**Status: Stage 1 approved on 2026-10-03 with changes (Windows instead of macOS, cheapest API, right-to-left Hebrew formatting, everything built from scratch). Stage 2 is complete: all nine parts (Chapters 0–32), six appendices, 33 Obsidian notes, every exercise with starter/solution/tests, and the Morning Brief reference implementation plus starter. Stage 3 (consistency review and readiness checklists) is done: see `00-stage1/08-stage3-consistency-review.md` and appendix ה. The master table of contents with per-chapter completion status lives in `book/README.md`.**

This directory will hold the complete course: a Hebrew textbook, per-chapter exercises with starter
and reference solutions, Obsidian-ready notes, the daily study schedule, and the final portfolio
project ("Morning Brief", a personalized morning-newsletter agent).

It lives in its own repository, separate from any work project: nothing here may contain employer code, names, or data.

## What exists now (Stage 1)

| File | Contents |
| --- | --- |
| `00-stage1/01-critical-review.md` | Review of the ChatGPT draft + DocDesk project: what to keep, shorten, remove; what is missing |
| `00-stage1/02-table-of-contents.md` | Proposed book structure (32 chapters in 9 parts), chapter-end apparatus, exercise→project reuse map |
| `00-stage1/03-daily-schedule.md` | 16 weeks / 80 study days, each with topic, objective, sections, time, exercise, done-criterion, "can explain" |
| `00-stage1/04-final-project.md` | Morning Brief: requirements, architecture, diagram, decisions vs. simpler alternatives, 9 milestones |
| `00-stage1/05-tech-stack.md` | The minimal stack and the reasoning, costs, free alternatives, what is deliberately excluded |
| `00-stage1/06-quality-checklist.md` | The quality-control checklist from the brief, answered |
| `00-stage1/07-decisions-2026-10-03.md` | Your answers to the open questions and what each one changed |

## Planned layout after approval (Stage 2)

```text
ai-engineering-course/
  README.md
  00-stage1/                 this review and plan
  book/README.md             master table of contents + completion status (Stage 2)
  book/CONVENTIONS.md        the Hebrew right-to-left formatting rules every chapter follows
  book/NN-<slug>.md          Hebrew chapters 00..32
  book/appendices/           glossary, troubleshooting, cost tracker, note templates, checklists, schedule (HE)
  exercises/chNN-<slug>/     README.md (goal, steps, checklist, hints), starter/, solution/, tests/
  obsidian/                  one short note per chapter, ready to drop into the vault
  project/morning-brief/     milestone briefs + starter templates + reference solution
  tools/build_html.py        renders book/*.md to site/*.html with proper RTL styling
  site/                      generated HTML (the comfortable way to read the book)
```

## Related material on this machine (not modified)

- `~/applied-ai-learning` — a 10-week scaffold created on 2026-09-26 (no commits, no remote).
  Not reused: you asked for everything to be built from scratch. It can be deleted.
- The ChatGPT draft and the DocDesk project zip reviewed in Stage 1 are not part of this repository;
  the course is built from scratch.
