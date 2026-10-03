# Formatting and writing conventions for the Hebrew book

Every chapter file follows these rules so that the book reads correctly right-to-left in three
places: the generated HTML (`site/`), Obsidian (with the RTL Support plugin), and GitHub's Markdown
preview.

## File skeleton

```markdown
---
direction: rtl
lang: he
title: "פרק 2: סביבת העבודה ב-Windows"
chapter: 2
part: "חלק א: התמצאות וסביבת עבודה"
---

<div dir="rtl" lang="he">

# פרק 2: סביבת העבודה ב-Windows

...chapter body in Markdown...

</div>
```

- `direction: rtl` in the front matter is read by Obsidian's "RTL Support" plugin.
- The `<div dir="rtl" lang="he">` wrapper, with a blank line after it and before the closing tag,
  makes GitHub and VS Code previews right-to-left. `tools/build_html.py` strips it and sets the
  direction on the `<html>` element instead.
- **Every fenced code block is wrapped** in `<div dir="ltr" align="left">` with a blank line after
  the opening tag and a blank line before the closing `</div>`. Markdown viewers that honor the
  chapter's `dir="rtl"` would otherwise right-align the code and wreck Python indentation (reader
  feedback, 2026-10-03). The site CSS and the Obsidian snippet add the same guarantee, but the
  wrapper is what works everywhere. `tools/wrap_ltr_blocks.py` adds missing wrappers idempotently;
  run it after writing a chapter.

  ```markdown
  <div dir="ltr" align="left">

  ```python
  print("left-to-right, indentation intact")
  ```

  </div>
  ```

## Structure of a chapter

1. Title: `# פרק N: <שם>`.
2. Opening paragraph (2–4 lines): what the chapter does and why it matters for the job.
3. `## מה נלמד בפרק` — 4–7 bullets. `## ידע מקדים` — which chapters it relies on.
4. Numbered sections `## N.1 <שם>`, subsections `### N.1.1 <שם>`. Every section is numbered so the
   schedule and other chapters can reference it.
5. Closing apparatus, always in this order and with these exact headings:
   `## סיכום`, `## מונחים לזכור` (table: מונח בעברית | באנגלית | במשפט אחד),
   `## טעויות נפוצות`, `## שאלות ראיון`, `## פתק Obsidian`, `## תרגיל`, `## העשרה אופציונלית`.
6. The Obsidian note is given as a blockquote in the chapter *and* as a file in `obsidian/`.
7. The exercise section states goal, time, prerequisites and completion criteria, and links to
   `exercises/chNN-<slug>/README.md`, which holds the full steps, starter, hints, solution and tests.

## Writing rules

- Short paragraphs (at most five lines). Parallel items go in bullets; comparisons go in tables.
- Second person feminine singular throughout (את, תריצי, שימי לב), matching the reader.
- Every technical term: Hebrew first, English in parentheses on first use in the chapter, for
  example "חלון הקשר (context window)". Afterwards use the Hebrew term, or the English identifier in
  backticks when it names something in code.
- A sentence, bullet or table cell never starts with a Latin word or a digit when it can be avoided;
  begin with a Hebrew word ("המונח `uv` ...", "הפקודה `uv run` ...").
- Hebrew prefix letters attach to a Latin word with a maqaf: ה־API, ב־PowerShell, ל־Obsidian.
- No em-dashes in Hebrew text; use a colon, a comma or parentheses. Quotation marks: „...” or "...".
- Numbers in Western digits. Units and currency after the number: 3 דקות, 0.30 דולר.
- Code, commands, file names, flags, JSON and model names appear only in backticks or fenced blocks.
  Comments inside code are short and in English. Explanations come after the block, in Hebrew.
- Commands are PowerShell, written without a prompt prefix so they can be copied as they are.
  Expected output is shown in its own fenced block labelled `text`.
- Callouts are blockquotes with a bold Hebrew label on the first line:
  `> **שימי לב:**`, `> **טעות נפוצה:**`, `> **מונח:**`, `> **ב־Windows:**`, `> **העשרה אופציונלית:**`.
- Cross-references: "ראי פרק 5, סעיף 5.3". Links to files in the repository use relative paths.
- Model names, prices and rate limits never appear hard-coded in prose as facts of the world; they
  are quoted "נכון לאוקטובר 2026" and live in `.env` or in appendix C.
- Honesty rule inherited into every exercise: a result the reader did not measure is never
  described as measured.

## Mixed-direction readability (added 2026-10-03 after reader feedback)

The reader found a note unreadable: several labelled items collapsed into one paragraph, dense with
English identifiers inside Hebrew text. Rules that prevent it:

- **One item per line means one list item.** Consecutive lines in a paragraph or blockquote merge
  when rendered. Anything meant to be read line by line is a bulleted list.
- **At most two English or code tokens per Hebrew sentence.** If a sentence needs more, change the
  shape: a table (Hebrew column + English column), a bulleted list with one token per bullet, or a
  Hebrew sentence followed by a left-to-right code block.
- **Commands never live inside Hebrew prose.** A single short token in backticks is fine; anything
  with spaces, flags or paths goes in a fenced block under the sentence that explains it.
- **Cheat sheets are English-only, in a `text` fence.** The Obsidian note of every chapter has two
  parts: Hebrew bullets for concepts, then an English-only `text` block for commands, identifiers and
  blanks to fill in. Never interleave the two.
- **Explain command sequences with a two-column table** (command | what it did), not a paragraph.
- **No arrows, pluses or slashes between words in Hebrew text** (←, →, +, /). Write the words.
- **Completion criteria, summaries and checklists are bullets**, Hebrew first, with any identifier at
  the end of the sentence.
- **Avoid long inline paths in sentences.** Say what the file is in Hebrew, then give the path at
  the end of the sentence or in a code block.

## Mermaid diagrams

Use fenced blocks labelled `mermaid`. The HTML build renders them in the browser; Obsidian renders
them natively. Keep node labels short and in English or transliterated Hebrew (Mermaid handles
Hebrew labels poorly).
