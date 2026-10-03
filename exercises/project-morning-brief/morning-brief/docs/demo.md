# Three-minute demo script

Backup ready: `out/brief-<date>.html` from a successful run, and `data/runs/<date>/run-report.md`.

- **0:00–0:20** — "Every morning I read forty articles from ten feeds to find the three that matter. Morning Brief does it
  for me. This is today's issue, generated at seven, for a few cents." (Screen: the HTML issue.)
- **0:20–1:00** — The diagram. "Nine stages. K is plain code; four M stages are single model calls with a schema; one A
  stage is a bounded agent that chooses which items to read. Everything else is a workflow because the code knows the
  next step."
- **1:00–1:50** — `uv run morning-brief run --offline` then `cat data/runs/<date>/run-report.md`. "Every model call is a
  traced event with tokens and cost; the report sums per stage. No article text in the trace by default."
- **1:50–2:30** — `docs/eval-latest.md`. "Fourteen labeled items for relevance, six for faithfulness with a judge I
  calibrated against my labels, eight duplicate pairs, five injection cases. These are the thresholds; this is the last run."
- **2:30–3:00** — "Two limits: one reader and public feeds only; and the judge is a model, so I hand-check ten answers a
  week. Next: ranking that learns from what I actually open. Code, eval and architecture notes are on GitHub."
