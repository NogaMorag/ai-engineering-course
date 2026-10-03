# Stage 3 — Consistency review and readiness checklists (2026-10-03)

Stage 3 of the brief: a final consistency pass over the whole course, plus the learning and
interview-readiness checklists. The checklists live in the book itself (appendix ה,
`book/appendices/e-checklists.md`) so the learner meets them on day 79; this file records what was
checked, what was found, and what was fixed.

## What the course contains at the end of Stage 2

| artifact | count | where |
| --- | --- | --- |
| chapters (Hebrew, full apparatus) | 33 (0–32) | `book/` |
| appendices | 6 (א–ו) | `book/appendices/` |
| Obsidian notes | 33 | `obsidian/` |
| exercise packages (starter / solution / tests / README) | 27 chapter exercises + 3 career exercise folders | `exercises/` |
| offline tests, chapter exercises | 168 passed, 2 skipped by design | mirrored learner project |
| capstone reference implementation | `morning-brief/`, 21 tests, 4-part eval, offline end-to-end run | `exercises/project-morning-brief/` |
| capstone starter | generated, 24 modules stubbed, tests are the spec | `exercises/project-morning-brief/morning-brief-starter/` |
| glossary terms | 278 | `book/appendices/a-glossary.md` (generated) |
| rendered site | 39 pages + index | `site/` |

## Automated checks (`tools/consistency_check.py`, final run: OK)

- every TOC row points at an existing file and is marked ✅;
- every chapter 1–32 has the nine apparatus headings in the fixed order;
- every fenced code block in chapters, appendices, notes and exercise READMEs is wrapped in an LTR div;
- every relative Markdown link resolves; every `[[note]]` link in `obsidian/` resolves;
- every chapter cross-reference ("פרק N") points at an existing chapter; every "יום N" is within 1–80;
- the exercise day blocks named in the chapters are in order (a shared boundary day is allowed; the
  project chapters share the project days);
- every exercise folder referenced by a chapter exists with a README and a solution/tests/cases/templates folder;
- no employer-related terms anywhere in the course.

## Manual spot checks and fixes

| check | finding | fix |
| --- | --- | --- |
| stray transliterations (פרומפט, אמבדינג, טרייס, אג'נט) | none; „טוקנים” is the accepted term | — |
| one English term, several Hebrew renderings (glossary collector) | 4 of 278: `max_output_tokens`, `open weights`, `prompt injection`, `time to first token` | standardized on the dominant rendering across chapters, notes and READMEs; glossary regenerated; 0 remaining |
| chapter exercise days vs. exercise README days | consistent for every chapter | — |
| schedule wording vs. Gemini Interactions API | D14–D19 still used the original draft's API names (fixed in Part 3) | recorded in `07-decisions-2026-10-03.md` |
| appendix D nested code fences broke the wrapper count | one template contained a fence inside a fence | inner fence replaced by a plain line |
| build tool and wrapper tool coverage of `book/appendices/` | both already covered the folder | — |

## Known limitations, recorded on purpose

- **No live run happened during authoring.** Every API call in the course was written against the
  installed SDK (shapes verified by introspection) and tested offline with fakes and fixtures; the
  reader's first live run on each chapter is the live check, and the troubleshooting appendix lists the
  expected error endings. The project's `make eval` is the first paid measurement.
- **Offline injection eval is not meaningful** (the fake model copies text); the harness says so.
- **Prices** (appendix ג, `PRICES`) were checked on 2026-10-03 and will drift; the tables name the date.
- **Appendix ו mirrors the English schedule's structure**; the per-day exercise text stays in
  `03-daily-schedule.md` to avoid a second source of truth.

## Readiness checklists

- Learning checklist, per part: appendix ה, first half.
- Interview-readiness checklist (ready / practised / written): appendix ה, second half.
- Day 79 ticks them; every monthly job-search review re-ticks them.
