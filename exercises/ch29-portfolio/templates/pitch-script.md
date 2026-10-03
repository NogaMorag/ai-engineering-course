# Three-minute demo script

Backup ready before you start: a saved issue + run report, or a recording of a successful run.
Every <placeholder> below is a number from *your* run report or eval report; say only numbers you measured.

**0:00–0:20 — the problem and the result.** (Screen: this morning's issue.)
"Every morning I read forty articles from ten feeds to find the three that matter to me. Morning Brief does that
for me: this is today's issue, generated at seven, for <X> cents."

**0:20–1:00 — the diagram.** (Screen: the pipeline.)
"Nine stages. The ones marked K are plain code — fetching, extraction, ranking, dedupe, delivery. Only four
calls go to a model, each with a schema. One stage, research, is an agent: it decides which items to read,
within six steps and a budget. Everything else is a workflow, because the code already knows the next step."

**1:00–1:50 — a run.** (Screen: terminal, `--offline` or a short real run; then the run report.)
"Here is a run. Every model call is a span in this trace: model, tokens, cost. The report says: <n> summaries,
<n> research runs, <X> dollars. No article text in the trace by default: that is a redaction decision."

**1:50–2:30 — the eval.** (Screen: the eval report table.)
"How do I know it works? Four parts: relevance on <n> labeled items, faithfulness with a judge I calibrated
against <n> of my own labels, <n> duplicate pairs, <n> injection cases, each with a threshold. Last run: <x of n>
faithful, <x of n> injection cases passed. The failure I know about is <one sentence>; the fix is <one sentence>."

**2:30–3:00 — limits and next.**
"Two limits: one user, public feeds only; and the judge is a model, so I re-check ten answers by hand every
week. Next: ranking that learns from what I actually opened. The code, the eval and the architecture notes are
on GitHub."

Timing log: take 1 ___  take 2 ___  take 3 ___
