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

## Stage 4 — self-review against the original brief (2026-10-03)

**Method.** The brief's requirements were rebuilt as a checklist (language, technical correctness, scope, math,
completeness, sequence, schedule, exercises, environment, final project, interview readiness, integrity). Every
chapter, exercise README, appendix and the capstone were read in full: chapters 0, 2 and appendices A, C, F plus all
code, data and SDK usage by the coordinator; chapters 1, 3–32 and appendices B, D, E by eight delegated reviewers
working one part each, with fixed instructions (conventions, terminology table, no code edits, flag-don't-guess), whose
reports were then verified and acted on by the coordinator. External facts were checked against the official Gemini
docs (pricing, models, embeddings, caching, Interactions API pages, terms), the GitHub releases API, PyPI and the
installed `google-genai` 2.28.0 / `chromadb` 1.5.9 sources. All chapter tests (169 passed, 2 skipped by design) and
capstone tests (24 passed) were re-run after the changes; no live API call was possible on this machine.

**Confirmed correct (no change).** Model IDs and free-tier status; `gemini-embedding-2` (768 dims, task instruction
in the text, auto-normalized truncation); the Interactions API parameter set and `response_format` shape; function
results as plain strings; `thinking_level` values; `tool_choice` values; `usage` fields incl. `total_tokens`; the
`requires_action`/`incomplete`/`budget_exceeded` statuses; the `thought` step type; status-code exception classes
(`RateLimitError`, `NotFoundError`, …); `HttpOptions` timeout/retry reaching the Interactions path; the
OpenAI-compatible base URL; pydantic 2.13 / pytest 9 / ruff 0.16 pins; Chroma `get_or_create_collection` keeping
existing metadata (proved by the passing test).

**Corrected — technical.**
- Cached-input prices were 25% of input instead of the official 10% (Flash-Lite $0.03, 3.8 Flash $0.075); every
  table, formula, illustrative report and expected output recomputed; 2027 prices noted.
- Streaming events are read via `event.event_type` (was `event.type`): chapter 11 code, starter, solution.
- SDK default retries on the Interactions path are 3 attempts, not 5 (stacked worst case 12, not 20): chapters 11, 23.
- Implicit prompt caching needs a 4,096-token prefix on the 3.x Flash models (official page); chapters 15, 22, 23,
  31, appendix C and the schedule now say so, the illustrated "cache hits" on 400–1,200-token prompts were replaced by
  honest zeros, and the day-29 check runs on the long-context prompt.
- Chapter 13 query labels were misaligned with the headline ids (generator renamed ids in place while iterating);
  generator fixed, data regenerated (headlines unchanged, 14 query lines corrected), README examples checked.
- GitHub Actions pins moved to current majors (checkout v7, setup-uv v10, cache v6, upload-artifact v7); the
  project's `actions/cache` path list was one space-separated line (matches nothing) and is now newline-separated.
- Chapter 25 job and the capstone CLI now run the versions pre-flight the prose promised (exit code 5, tests added).
- Capstone: `resilient_complete` is wired into summarize, score and the intro (fallback model, then degrade);
  summaries store real token counts and cost (were zeros); the issue templates print a note on an empty day; the
  eval harness unpacks the new return value; tests added.
- Chapter 16: Cohen's kappa shipped ready in the starter (intuition-first chapter, formula in the cheat sheet);
  judge tokens counted in the run cost; the case-count test accepts added cases; `run_checks` moved to day 31.
- Chapter 18: a `--judge` tier that skips like `--live`; cassettes record which model answered; the heavy
  `ask_notes` cassette step marked optional for the checkpoint.
- Chapter 11 tests import the day-19 CLI lazily; chapter 9 starter imports before TODO 2; chapter 3 classifier
  output deterministic; chapter 12 embedder comment; chapter 14 store disables Chroma telemetry as the text says;
  `n_results` behaviour stated as warn-and-clamp (chromadb 1.5).
- Unsupported claims softened or sourced: "evaluation is the rarest skill" (ch 1, now sourced to a 2026 postings
  analysis), `count_tokens` "not billed" (not on the price list; counts against the rate limit), anthropomorphic
  phrasings across chapters 4–6, 10, 19, 24, 26.

**Corrected — program and pedagogy.**
- Day 0 (installations only) added before week 1; day 2 is the project, key and first call (~90 min).
- Appendix F is now the complete Hebrew day-by-day plan (objective, reading, time, task, completion criterion, what
  you can explain, for days 0–80 plus the checkpoint table); the English file is its source.
- Section splits aligned to the chapters and to the exercise day splits for days 15–16, 23–24, 27–29, 31–32,
  40–42, 44–46, 71–72; the chapter 6 quiz moved to day 10; line counting and the LangGraph decision note moved from
  day 40 to day 42.
- Every coding exercise README now carries the full template (goal, time, prerequisites, files, commands, starter,
  steps, expected output, checklist, common mistakes and fixes, hints, solution with why, what it demonstrates);
  `tools/consistency_check.py` enforces the section set and the appendix-F day coverage.
- Interview questions: duplicates and recitation questions rewritten; up to two realistic follow-ups per chapter;
  the question bank carries a `follow_up` per question (rendered as **המשך:**).
- Hidden prerequisites surfaced: asyncio primitives (ch 19), Python features used in Part C (ch 7 box), the
  chapter-2 module imported by chapter 5, Chroma/BM25 modules imported across Part D.
- Scope trims: Transformer component table (ch 5) and training jargon (ch 4) moved to optional enrichment;
  chapter 26 gained the selection criteria beyond the eval score (context window, rate limits, structured output,
  Hebrew, data policy, licence, leaderboards, LoRA/distillation).
- Platform: Windows/PowerShell stays primary per the Stage 1 answer; a Mac equivalents table (ch 2 §2.13), Mac rows
  in appendix B, a cron/launchd note (ch 25) and `run_daily.sh` twins were added because the review brief says Mac.
- Language: calques, gender slips, mixed-direction sentences, arrows/pluses/slashes between Hebrew words, vague
  instructions and inconsistent renderings fixed throughout; terminology policy recorded in `CONVENTIONS.md`.

**Still requires live verification (no key on this machine).** That `max_output_tokens` truncation yields status
`incomplete`; the default `thinking_level` of Flash-Lite; whether Flash-Lite has a published implicit-cache minimum;
the exact free-tier rate limits (shown only in AI Studio); the cassette-recording recipes of chapter 18 and the
calibration run of chapter 16 (their offline halves were executed, the paid halves were not); the first scheduled
GitHub Actions run.
